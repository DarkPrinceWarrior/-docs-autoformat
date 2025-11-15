import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadDocument } from '../services/api';
import './FileUploader.css';

const FileUploader = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];

    if (!file) {
      setError('Пожалуйста, выберите файл');
      return;
    }

    if (!file.name.endsWith('.docx')) {
      setError('Поддерживаются только файлы формата .docx');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await uploadDocument(file);
      setSuccess(`Файл "${file.name}" успешно загружен! Идет обработка...`);

      if (onUploadSuccess) {
        onUploadSuccess(result);
      }

      // Очищаем сообщение об успехе через 5 секунд
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке файла');
    } finally {
      setUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: false,
  });

  return (
    <div className="file-uploader">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${uploading ? 'uploading' : ''}`}
      >
        <input {...getInputProps()} />

        {uploading ? (
          <div className="upload-status">
            <div className="spinner"></div>
            <p>Загрузка и обработка документа...</p>
          </div>
        ) : (
          <>
            <svg
              className="upload-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>

            {isDragActive ? (
              <p className="drop-text">Отпустите файл для загрузки...</p>
            ) : (
              <>
                <p className="drop-text">
                  Перетащите файл .docx сюда или нажмите для выбора
                </p>
                <p className="drop-hint">
                  Максимальный размер файла: 10 МБ
                </p>
              </>
            )}
          </>
        )}
      </div>

      {error && (
        <div className="message error-message">
          <span className="message-icon">⚠️</span>
          {error}
        </div>
      )}

      {success && (
        <div className="message success-message">
          <span className="message-icon">✓</span>
          {success}
        </div>
      )}
    </div>
  );
};

export default FileUploader;
