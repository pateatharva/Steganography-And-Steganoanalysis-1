from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
import torch
from PIL import Image
import io
import os
import numpy as np
from torchvision import transforms
from datetime import timedelta
import uuid
from torch import serialization as torch_serialization
from models.ganstego import (
    AdvancedGenerator, 
    AdvancedDecoder, 
    AdvancedDiscriminator,
    text_to_bits,
    bits_to_text
)

app = Flask(__name__)
# Allow frontend at localhost:3000 by default; adjust as needed
CORS(app, resources={r"*": {"origins": "*"}})

# Initialize SQLAlchemy if available
from db_models import db, User, ProcessingHistory
from dotenv import load_dotenv
import os
load_dotenv()

# Configure Flask-JWT-Extended (fixed dev secret to avoid env mismatches)
app.config['JWT_SECRET_KEY'] = 'dev-secret-fixed'
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_CSRF_CHECK_FORM'] = False  # Disable CSRF for Bearer tokens
jwt = JWTManager(app)

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    try:
        print(f"[JWT] Invalid token: {error}", flush=True)
    except Exception:
        pass
    # Temporarily expose reason to help diagnose during development
    return jsonify({'error': f'Invalid token: {error}'}), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({'error': 'Missing authorization header'}), 401

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///stegano.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'
db.init_app(app)

# Model initialization
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
message_len = 256

# Initialize models
generator = AdvancedGenerator(message_len).to(device)
decoder = AdvancedDecoder(message_len).to(device)
discriminator = AdvancedDiscriminator().to(device)

# Ensure instance and upload directories exist
INSTANCE_DIR = os.path.join(os.path.dirname(__file__), 'instance')
UPLOAD_DIR = os.path.join(INSTANCE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowlist numpy scalar for safe torch.load when weights_only=True
try:
    torch_serialization.add_safe_globals([np._core.multiarray.scalar, np.dtype])
except Exception:
    pass

# Load the saved model
model_path = os.path.join(os.path.dirname(__file__), 'models', 'final_ganstego.pth')
if os.path.exists(model_path):
    try:
        print("[Startup] Loading model checkpoint...", flush=True)
        # Fallback to legacy load for this checkpoint
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        print("[Startup] Checkpoint loaded, applying state dicts...", flush=True)
        if isinstance(checkpoint, dict):
            generator.load_state_dict(checkpoint['generator'])
            decoder.load_state_dict(checkpoint['decoder'])
            discriminator.load_state_dict(checkpoint['discriminator'])
        else:
            print("Model format is different, trying direct load...")
            if hasattr(checkpoint, 'generator'):
                generator = checkpoint.generator
            if hasattr(checkpoint, 'decoder'):
                decoder = checkpoint.decoder
            if hasattr(checkpoint, 'discriminator'):
                discriminator = checkpoint.discriminator
        print("Model loaded successfully!", flush=True)
    except Exception as e:
        print(f"Warning: Error loading model: {str(e)}", flush=True)
else:
    print(f"Warning: Model file {model_path} not found!", flush=True)

# Set models to evaluation mode
generator.eval()
decoder.eval()
discriminator.eval()

# Image transformations
transform = transforms.Compose([
    transforms.Resize((96, 96)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# ===== IMAGE QUALITY METRICS =====
def calculate_psnr(img1, img2):
    """Calculate Peak Signal-to-Noise Ratio between two images"""
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return 100.0
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return round(psnr, 2)

def calculate_ssim(img1, img2):
    """Calculate Structural Similarity Index between two images"""
    # Convert to grayscale if needed
    if len(img1.shape) == 3:
        img1_gray = np.mean(img1, axis=2)
        img2_gray = np.mean(img2, axis=2)
    else:
        img1_gray = img1
        img2_gray = img2
    
    # Constants for SSIM
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2
    
    # Calculate means
    mu1 = np.mean(img1_gray)
    mu2 = np.mean(img2_gray)
    
    # Calculate variances and covariance
    sigma1_sq = np.var(img1_gray)
    sigma2_sq = np.var(img2_gray)
    sigma12 = np.cov(img1_gray.flatten(), img2_gray.flatten())[0, 1]
    
    # SSIM formula
    ssim = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
           ((mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2))
    
    return round(ssim, 4)

def calculate_ber(original_bits, extracted_bits):
    """Calculate Bit Error Rate between original and extracted bits"""
    if len(original_bits) != len(extracted_bits):
        return 1.0
    
    errors = sum(o != e for o, e in zip(original_bits, extracted_bits))
    ber = errors / len(original_bits)
    return round(ber, 6)

def get_image_stats(image_array):
    """Get basic statistics about an image"""
    return {
        'mean': round(float(np.mean(image_array)), 2),
        'std': round(float(np.std(image_array)), 2),
        'min': round(float(np.min(image_array)), 2),
        'max': round(float(np.max(image_array)), 2)
    }

def preprocess_image(image):
    return transform(image)

def postprocess_image(tensor):
    # Denormalize and convert to PIL Image
    tensor = tensor * 0.5 + 0.5
    tensor = tensor.squeeze(0).permute(1, 2, 0)
    tensor = tensor.detach().cpu().numpy()
    tensor = np.clip(tensor * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(tensor)

# Static serving for uploaded files (must be defined at import time)
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route('/steganography/hide', methods=['POST'])
def hide_message():
    print("[HIDE_MESSAGE] Endpoint called")
    if 'image' not in request.files or 'message' not in request.form:
        print("[HIDE_MESSAGE] Missing image or message")
        return jsonify({'success': False, 'error': 'Missing image or message'}), 400

    try:
        print("[HIDE_MESSAGE] Processing request...")
        # Load and process cover image
        cover_image = Image.open(request.files['image']).convert('RGB')
        message = request.form['message'][:32].ljust(32)  # Ensure message is 32 chars
        
        # Store original cover image as numpy array for metrics
        cover_array = np.array(cover_image)

        # Prepare inputs for model
        image_tensor = preprocess_image(cover_image).unsqueeze(0).to(device)
        message_tensor = text_to_bits(message, 32).unsqueeze(0).to(device)

        with torch.no_grad():
            # Generate stego image
            stego_tensor = generator(image_tensor, message_tensor)
            stego_image = postprocess_image(stego_tensor)
            
            # Convert stego to numpy for metrics
            stego_array = np.array(stego_image)
            
            # Resize cover to match stego dimensions if needed
            if cover_array.shape != stego_array.shape:
                cover_image_resized = cover_image.resize(stego_image.size)
                cover_array = np.array(cover_image_resized)

            # Calculate COVER image metrics (comparing to itself - should be perfect)
            cover_psnr = 100.0  # Perfect PSNR for original
            cover_ssim = 1.0     # Perfect SSIM for original
            cover_ber = 0.0      # No error for original
            
            # Calculate STEGO image quality metrics (comparing stego to cover)
            stego_psnr = calculate_psnr(cover_array, stego_array)
            stego_ssim = calculate_ssim(cover_array, stego_array)
            
            # Extract message to calculate BER for stego
            extracted_bits_tensor = decoder(stego_tensor)
            original_bits = message_tensor.cpu().numpy().flatten()
            extracted_bits = (extracted_bits_tensor > 0.5).cpu().numpy().flatten()
            stego_ber = calculate_ber(original_bits, extracted_bits)
            
            # Get image statistics
            cover_stats = get_image_stats(cover_array)
            stego_stats = get_image_stats(stego_array)

            # Save stego image to file
            filename = f"stego_{uuid.uuid4().hex}.png"
            file_path = os.path.join(UPLOAD_DIR, filename)
            print(f"[HIDE_MESSAGE] Saving stego image to: {file_path}")
            stego_image.save(file_path, format='PNG')

            # Save cover image for comparison
            cover_filename = f"cover_{uuid.uuid4().hex}.png"
            cover_path = os.path.join(UPLOAD_DIR, cover_filename)
            print(f"[HIDE_MESSAGE] Saving cover image to: {cover_path}")
            cover_image.save(cover_path, format='PNG')
            print("[HIDE_MESSAGE] Images saved successfully")

        # Optionally record history if JWT token is provided
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            try:
                user_id = int(user_id) if user_id is not None else None
            except (TypeError, ValueError):
                user_id = None
            if user_id:
                with app.app_context():
                    user = User.query.get(user_id)
                    if user:
                        hist = ProcessingHistory(
                            user_id=user.id,
                            operation_type='encode',
                            image_path=f"/uploads/{filename}",
                            message_length=len(message),
                            success=True
                        )
                        db.session.add(hist)
                        db.session.commit()
        except Exception:
            # No token provided or invalid token - skip history recording
            pass

        # Return comprehensive metrics with separate cover and stego metrics
        response_data = {
            'success': True,
            'stego_image': f'/uploads/{filename}',
            'cover_image': f'/uploads/{cover_filename}',
            'message': message,
            'cover_metrics': {
                'psnr': float(cover_psnr),
                'ssim': float(cover_ssim),
                'ber': float(cover_ber)
            },
            'stego_metrics': {
                'psnr': float(stego_psnr),
                'ssim': float(stego_ssim),
                'ber': float(stego_ber)
            },
            'cover_stats': cover_stats,
            'stego_stats': stego_stats,
            'model_performance': {
                'quality_score': round((stego_psnr / 50) * 100, 2),
                'similarity_score': round(stego_ssim * 100, 2),
                'embedding_accuracy': round((1 - stego_ber) * 100, 2)
            }
        }
        print(f"[HIDE_MESSAGE] Returning response with cover and stego metrics")
        return jsonify(response_data), 200

    except Exception as e:
        print(f"[HIDE_MESSAGE ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/steganalysis/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Missing image'}), 400

    try:
        image = Image.open(request.files['image']).convert('RGB')
        image_tensor = preprocess_image(image).unsqueeze(0).to(device)

        with torch.no_grad():
            disc_output = discriminator(image_tensor)
            is_stego = torch.sigmoid(disc_output).item() < 0.5  # Less than 0.5 means it's more likely to be a stego image

        return jsonify({
            'is_stego': bool(is_stego),
            'confidence': float(abs(0.5 - torch.sigmoid(disc_output).item()) * 2)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Register blueprints for auth and API routes
try:
    from routes.auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    print("[STARTUP] Auth blueprint registered successfully", flush=True)
except Exception as e:
    print(f"[ERROR] Failed to register auth blueprint: {e}", flush=True)

try:
    from routes.api import api as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    print("[STARTUP] API blueprint registered successfully", flush=True)
except Exception as e:
    print(f"[ERROR] Failed to register API blueprint: {e}", flush=True)

@app.route('/steganography/extract', methods=['POST'])
def extract_message():
    if 'image' not in request.files:
        return jsonify({'error': 'Missing image'}), 400

    try:
        image = Image.open(request.files['image']).convert('RGB')
        image_tensor = preprocess_image(image).unsqueeze(0).to(device)

        with torch.no_grad():
            decoded_bits = decoder(image_tensor).squeeze(0).cpu().round()
            extracted_message = bits_to_text(decoded_bits)

        # Optionally record history if JWT token is provided
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            try:
                user_id = int(user_id) if user_id is not None else None
            except (TypeError, ValueError):
                user_id = None
            if user_id:
                with app.app_context():
                    user = User.query.get(user_id)
                    if user:
                        hist = ProcessingHistory(
                            user_id=user.id,
                            operation_type='decode',
                            image_path=None,
                            message_length=len(extracted_message or ''),
                            success=True
                        )
                        db.session.add(hist)
                        db.session.commit()
        except Exception:
            # No token provided or invalid token - skip history recording
            pass

        return jsonify({'message': extracted_message})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure DB exists
    with app.app_context():
        db.create_all()

    app.run(debug=False)