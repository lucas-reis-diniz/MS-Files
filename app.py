// Importando bibliotecas necessárias
const express = require('express');
const multer = require('multer');
const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

mongoose.connect('mongodb://localhost:27017/file_uploads', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

const FileSchema = new mongoose.Schema({
  filename: String,
  originalname: String,
  size: Number,
  uploadDate: { type: Date, default: Date.now },
  status: { type: String, default: 'Uploaded' },
});

const FileModel = mongoose.model('File', FileSchema);

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, `${Date.now()}-${file.originalname}`);
  },
});

const upload = multer({ storage });

app.use(express.json());

app.post('/upload', upload.single('file'), async (req, res) => {
  try {
    const { file } = req;
    const fileData = new FileModel({
      filename: file.filename,
      originalname: file.originalname,
      size: file.size,
    });

    await fileData.save();
    res.status(201).json({ message: 'File uploaded successfully', file: fileData });
  } catch (error) {
    res.status(500).json({ message: 'Error uploading file', error });
  }
});

app.post('/process/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const fileRecord = await FileModel.findById(id);

    if (!fileRecord) {
      return res.status(404).json({ message: 'File not found' });
    }

    const filePath = path.join(__dirname, 'uploads', fileRecord.filename);
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    const processedContent = fileContent.toUpperCase();

    const processedPath = path.join(
      __dirname,
      'uploads',
      `processed-${fileRecord.filename}`
    );
    fs.writeFileSync(processedPath, processedContent);

    fileRecord.status = 'Processed';
    await fileRecord.save();

    res.status(200).json({
      message: 'File processed successfully',
      processedFile: `processed-${fileRecord.filename}`,
    });
  } catch (error) {
    res.status(500).json({ message: 'Error processing file', error });
  }
});

app.get('/files', async (req, res) => {
  try {
    const files = await FileModel.find();
    res.status(200).json(files);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching files', error });
  }
});

app.use('/uploads', express.static(path.join(__dirname, 'uploads')));


app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
