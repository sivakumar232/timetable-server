// models/Timetable.js

const mongoose = require('mongoose');

const TimetableSchema = new mongoose.Schema({
    // A user-friendly name, e.g., "Fall 2025 Final"
    name: {
        type: String,
        required: true,
    },
    // The main JSON data of the generated timetable
    timetableData: {
        type: Object,
        required: true,
    },
    // A reference to the Admin user who created this timetable
    adminId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
    },
}, { timestamps: true });

const Timetable = mongoose.model('Timetable', TimetableSchema);

module.exports = Timetable;