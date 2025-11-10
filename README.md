# Steganography And Steganoanalysis

A full-stack web application for hiding messages in images (steganography) and detecting hidden content (steganalysis) using GAN-based deep learning models.

## Features

### Steganography
- Hide secret messages within images
- GAN-based encoding for imperceptible modifications
- Real-time PSNR and SSIM metrics display
- Download stego images with hidden messages

### Decoder
- Extract hidden messages from stego images
- Confidence score for extraction reliability
- Support for multiple image formats

### Steganalysis
- Detect whether an image contains hidden data
- Confidence percentage for detection
- AI-powered analysis using discriminator model

## Tech Stack

### Backend
- **Python 3.x**
- **Flask** - Web framework
- **PyTorch** - Deep learning framework
- **Firebase Admin** - Authentication
- **Pillow** - Image processing

### Frontend
- **React.js** - UI framework
- **Material-UI** - Component library
- **Axios** - HTTP client
- **React Router** - Navigation
- **Firebase** - Authentication

## Project Structure

```
.
├── backend/
│   ├── app.py                  # Flask application entry point
│   ├── models/
│   │   ├── ganstego.py        # GAN model architecture
│   │   └── final_ganstego.pth # Trained model weights
│   ├── routes/
│   │   ├── api.py             # Steganography & Steganalysis endpoints
│   │   └── auth.py            # Authentication endpoints
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Steganography.js  # Hide messages
│   │   │   ├── Decoder.js        # Extract messages
│   │   │   ├── Steganalysis.js   # Detect stego images
│   │   │   ├── Login.js          # User login
│   │   │   └── Register.js       # User registration
│   │   ├── App.js
│   │   └── firebase.js         # Firebase configuration
│   └── package.json            # Node dependencies
│
└── README.md
```

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- Firebase account (for authentication)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Firebase:
   - Place your Firebase service account JSON file in the backend directory
   - Update `firebase_admin_setup.py` with your credentials

5. Run the Flask server:
```bash
python app.py
```
The backend will run on `http://127.0.0.1:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure Firebase:
   - Update `src/firebase.js` with your Firebase project configuration

4. Start the development server:
```bash
npm start
```
The frontend will run on `http://localhost:3000`

## Usage

1. **Register/Login**: Create an account or login with existing credentials

2. **Hide Message** (Steganography):
   - Upload a cover image
   - Enter your secret message
   - Click "Hide Message"
   - View PSNR and SSIM quality metrics
   - Download the stego image

3. **Extract Message** (Decoder):
   - Upload a stego image
   - Click "Extract Message"
   - View the hidden message and confidence score

4. **Detect Stego Images** (Steganalysis):
   - Upload any image
   - Click "Analyze Image"
   - See if the image contains hidden data with confidence percentage

## Metrics Explained

- **PSNR (Peak Signal-to-Noise Ratio)**: Measures image quality after embedding (higher is better, 43-52 dB)
- **SSIM (Structural Similarity Index)**: Measures perceptual similarity (higher is better, 0.97-0.995)
- **Confidence**: Reliability score for extraction/detection (85-100%)

## API Endpoints

### Steganography
- `POST /steganography/hide` - Hide message in image
- `POST /steganography/extract` - Extract message from stego image

### Steganalysis
- `POST /steganalysis/analyze` - Detect hidden data in image

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

## Model Architecture

The project uses a GAN-based architecture:
- **Generator (Encoder)**: Embeds secret messages into images
- **Decoder**: Extracts hidden messages from stego images
- **Discriminator**: Detects whether images contain hidden data

## License

This project is for educational purposes.

## Contributors

Developed as part of a Steganography and Steganalysis research project.

## Support

For issues or questions, please open an issue in the GitHub repository.
