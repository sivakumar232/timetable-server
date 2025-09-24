const express = require('express');
const cors = require('cors');
const multer = require('multer');
const axios = require('axios');
const FormData = require('form-data');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
require('dotenv').config();
const app = express();
const PORT = process.env.PORT || 3001;
const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5000';
const User = require('./models/User'); 
const Timetable = require('./models/Timetable'); 
app.use(cors()); // Allows requests from your React app
app.use(express.json()); // Allows parsing of JSON in request bodies

// 3. DATABASE CONNECTION
mongoose.connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
}).then(() => console.log('MongoDB connected successfully.'))
  .catch(err => console.error('MongoDB connection error:', err));


// 5. AUTHENTICATION ROUTES (Public)

// --- REGISTRATION ROUTEx   ---
app.post('/api/register', async (req, res) => {
    try {
        const { email, password, institution, role } = req.body;

        // Check if user already exists
        let user = await User.findOne({ email });
        if (user) {
            return res.status(400).json({ msg: 'User with this email already exists' });
        }

        // Hash the password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // Create and save the new user
        user = new User({
            email,
            password: hashedPassword,
            institution,
            role,
        });
        await user.save();
        
                // Create and sign a JWT
            // In both /api/login and /api/register
        // In both /api/login and /api/register
        const payload = { user: { id: user.id, role: user.role } }; // <-- Add user.role here
        const token = jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1h' });
        res.status(201).json({ token });

    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
});

// --- LOGIN ROUTE ---
app.post('/api/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        // Check if user exists
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(400).json({ msg: 'Invalid credentials' });
        }

        // Compare passwords
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(400).json({ msg: 'Invalid credentials' });
        }

        // Create and sign a JWT
        const payload = { user: { id: user.id } };
        const token = jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1h' });

        res.json({ token });

    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
});


// 6. AUTH MIDDLEWARE (For protecting routes)
const authMiddleware = (req, res, next) => {
    // Get token from header
    const token = req.header('Authorization')?.split(' ')[1]; // "Bearer TOKEN"

    // Check if not token
    if (!token) {
        return res.status(401).json({ msg: 'No token, authorization denied' });
    }

    // Verify token
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded.user;
        next();
    } catch (err) {
        res.status(401).json({ msg: 'Token is not valid' });
    }
};

app.get('/api/me', authMiddleware, async (req, res) => {
    try {
        // req.user is added by the authMiddleware
        const user = await User.findById(req.user.id).select('-password'); // Exclude password
        if (!user) {
            return res.status(404).json({ msg: 'User not found' });
        }
        res.json(user);
    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
});

// 7. PROTECTED ROUTE EXAMPLE
// This route can only be accessed if a valid JWT is provided.
app.get('/api/dashboard', authMiddleware, async (req, res) => {
    try {
        // req.user is available here from the authMiddleware
        const user = await User.findById(req.user.id).select('-password');
        res.json({ 
            message: `Welcome to the dashboard, ${user.email}!`,
            userData: user 
        });
    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server Error');
    }
});
// server.js

// ... (after your other API routes)

// --- SAVE A TIMETABLE TO THE DATABASE ---
// server.js

// --- SAVE A BATCH OF TIMETABLES TO THE DATABASE ---
app.post('/api/timetables/save-batch', authMiddleware, async (req, res) => {
    // Check if the user is an admin
    const adminUser = await User.findById(req.user.id);
    if (!adminUser || adminUser.role !== 'admin') {
        return res.status(403).json({ msg: 'Forbidden: Only admins can save timetables.' });
    }

    try {
        const { timetableData } = req.body; // Expecting the full finalTimetable object
        const timetablesToSave = timetableData.timetables;

        if (!timetablesToSave || Object.keys(timetablesToSave).length === 0) {
            return res.status(400).json({ msg: 'No timetables provided to save.' });
        }

        // 1. Prepare an array of all the documents we want to create
        const documentsToInsert = Object.entries(timetablesToSave).map(([batchName, singleTimetableData]) => ({
            name: batchName, // Use the section name (e.g., "CSE-A") as the name
            timetableData: singleTimetableData,
            adminId: req.user.id,
        }));

        // 2. Insert all documents into the database in one go (very efficient)
        const insertedTimetables = await Timetable.insertMany(documentsToInsert);

        // 3. Get the IDs of all the newly created timetables
        const newTimetableIds = insertedTimetables.map(t => t._id);

        // 4. Add all the new timetable IDs to the admin's user document
        adminUser.timetables.push(...newTimetableIds);
        await adminUser.save();

        res.status(201).json({ success: true, msg: `${insertedTimetables.length} timetables saved successfully!` });

    } catch (err) {
        console.error('Error saving timetable batch:', err.message);
        res.status(500).send('Server Error');
    }
});







//MODEL CODE 
// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 16 * 1024 * 1024, // 16MB limit
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'text/csv' || file.mimetype === 'application/json') {
      cb(null, true);
    } else {
      cb(new Error('Only CSV and JSON files are allowed'), false);
    }
  }
});

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:3000', 'http://127.0.0.1:5173'],
  credentials: true
}));
app.use(express.json({ limit: '16mb' }));
app.use(express.urlencoded({ extended: true, limit: '16mb' }));


// Health check endpoint
app.get('/api/health', async (req, res) => {
  try {
    // Check if Flask API is running
    const flaskResponse = await axios.get(`${FLASK_API_URL}/api/health`);
    
    res.json({
      success: true,
      message: 'Express middleware is running',
      flask_status: flaskResponse.data,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Express middleware is running, but Flask API is not reachable',
      flask_error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});




// Get user preferences template
app.get('/api/user-preferences-template', async (req, res) => {
  try {
    const response = await axios.get(`${FLASK_API_URL}/api/user-preferences-template`);
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching preferences template:', error.message);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch user preferences template',
      details: error.response?.data || error.message
    });
  }
});

// Convert CSV to JSON endpoint
app.post('/api/convert-csv-to-json', upload.fields([
  { name: 'courses_csv', maxCount: 1 },
  { name: 'faculty_csv', maxCount: 1 },
  { name: 'classrooms_csv', maxCount: 1 },
  { name: 'batches_csv', maxCount: 1 }
]), async (req, res) => {
  try {
    // Validate that all required files are present
    const requiredFiles = ['courses_csv', 'faculty_csv', 'classrooms_csv', 'batches_csv'];
    const missingFiles = requiredFiles.filter(file => !req.files[file]);
    
    if (missingFiles.length > 0) {
      return res.status(400).json({
        success: false,
        error: `Missing required files: ${missingFiles.join(', ')}`
      });
    }

    // Create FormData for Flask API
    const formData = new FormData();
    
    requiredFiles.forEach(fileKey => {
      const file = req.files[fileKey][0];
      formData.append(fileKey, file.buffer, {
        filename: file.originalname,
        contentType: file.mimetype
      });
    });

    // Forward to Flask API
    const response = await axios.post(`${FLASK_API_URL}/api/convert-csv-to-json`, formData, {
      headers: {
        ...formData.getHeaders(),
      },
      maxContentLength: Infinity,
      maxBodyLength: Infinity
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error converting CSV to JSON:', error.message);
    
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(413).json({
        success: false,
        error: 'File too large. Maximum size is 16MB per file.'
      });
    }

    res.status(error.response?.status || 500).json({
      success: false,
      error: 'Failed to convert CSV to JSON',
      details: error.response?.data || error.message
    });
  }
});

// Validate data endpoint
app.post('/api/validate-data', async (req, res) => {
  try {
    const response = await axios.post(`${FLASK_API_URL}/api/validate-data`, req.body, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error validating data:', error.message);
    res.status(error.response?.status || 500).json({
      success: false,
      error: 'Failed to validate data',
      details: error.response?.data || error.message
    });
  }
});

// Generate timetable endpoint
app.post('/api/generate-timetable', async (req, res) => {
  try {
    // Log the request for debugging
    console.log('Received timetable generation request');
    console.log('Institution data keys:', Object.keys(req.body.institution_data || {}));
    console.log('User preferences:', Object.keys(req.body.user_preferences || {}));
    
    const response = await axios.post(`${FLASK_API_URL}/api/generate-timetable`, req.body, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 300000 // 5 minutes timeout for timetable generation
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error generating timetable:', error.message);
    
    if (error.code === 'ECONNABORTED') {
      return res.status(408).json({
        success: false,
        error: 'Timetable generation timed out. Please try with smaller parameters.',
        timeout: true
      });
    }

    res.status(error.response?.status || 500).json({
      success: false,
      error: 'Failed to generate timetable',
      details: error.response?.data || error.message
    });
  }
});

// Generate multi-section timetable endpoint
app.post('/api/generate-multi-section-timetable', async (req, res) => {
  try {
    console.log('Received multi-section timetable generation request');
    
    const response = await axios.post(`${FLASK_API_URL}/api/generate-multi-section-timetable`, req.body, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 300000 // 5 minutes timeout
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error generating multi-section timetable:', error.message);
    
    if (error.code === 'ECONNABORTED') {
      return res.status(408).json({
        success: false,
        error: 'Multi-section timetable generation timed out. Please try with smaller parameters.',
        timeout: true
      });
    }

    res.status(error.response?.status || 500).json({
      success: false,
      error: 'Failed to generate multi-section timetable',
      details: error.response?.data || error.message
    });
  }
});

// Debug endpoint
app.post('/api/debug', async (req, res) => {
  try {
    const response = await axios.post(`${FLASK_API_URL}/api/debug`, req.body, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error in debug endpoint:', error.message);
    res.status(error.response?.status || 500).json({
      success: false,
      error: 'Debug endpoint failed',
      details: error.response?.data || error.message
    });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(413).json({
        success: false,
        error: 'File too large. Maximum size is 16MB per file.'
      });
    }
    return res.status(400).json({
      success: false,
      error: `File upload error: ${error.message}`
    });
  }

  res.status(500).json({
    success: false,
    error: 'Internal server error',
    message: error.message
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
    availableEndpoints: [
      'GET /api/health',
      'GET /api/user-preferences-template',
      'POST /api/convert-csv-to-json',
      'POST /api/validate-data',
      'POST /api/generate-timetable',
      'POST /api/generate-multi-section-timetable',
      'POST /api/debug'
    ]
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Express middleware server running on port ${PORT}`);
  console.log(`Forwarding requests to Flask API at ${FLASK_API_URL}`);
  console.log('Available endpoints:');
  console.log('  GET  /api/health');
  console.log('  GET  /api/user-preferences-template');
  console.log('  POST /api/convert-csv-to-json');
  console.log('  POST /api/validate-data');
  console.log('  POST /api/generate-timetable');
  console.log('  POST /api/generate-multi-section-timetable');
  console.log('  POST /api/debug');
});

module.exports = app;