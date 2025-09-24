// models/User.js

const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
    email: {
        type: String,
        required: true,
        unique: true,
        lowercase: true,
    },
    password: {
        type: String,
        required: true,
    },
    institution: {
        type: String,
        required: true,
    },
    role: {
        type: String,
        required: true,
        enum: ['admin', 'faculty', 'student'],
    },

    // --- ADD THIS NEW FIELD ---
    // This will store an array of IDs linking to documents in the 'timetables' collection
    timetables: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Timetable'
    }]
    // -------------------------

}, { timestamps: true });

const User = mongoose.model('User', UserSchema);

module.exports = User;