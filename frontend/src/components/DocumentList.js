import React, { useEffect, useState } from 'react';
import { getDocuments, getDocumentStatus, downloadDocument } from '../services/api';
import DocumentItem from './DocumentItem';
import './DocumentList.css';

const DocumentList = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const data = await getDocuments();
      setDocuments(data);
      setError(null);
    } catch (err) {
      setError('Ошибка при загрузке списка документов');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();

    // Обновляем список каждые 5 секунд для отслеживания статусов
    const interval = setInterval(fetchDocuments, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleDownload = async (documentId, filename) => {
    try {
      const blob = await downloadDocument(documentId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `formatted_${filename}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Ошибка при скачивании:', err);
      alert('Ошибка при скачивании документа');
    }
  };

  if (loading && documents.length === 0) {
    return (
      <div className="document-list">
        <h2>История документов</h2>
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Загрузка...</p>
        </div>
      </div>
    );
  }

  if (error && documents.length === 0) {
    return (
      <div className="document-list">
        <h2>История документов</h2>
        <div className="error-container">
          <p>{error}</p>
          <button onClick={fetchDocuments} className="retry-button">
            Повторить
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="document-list">
      <h2>История документов</h2>

      {documents.length === 0 ? (
        <div className="empty-state">
          <svg
            className="empty-icon"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p>Документов пока нет</p>
          <p className="empty-hint">Загрузите первый документ для обработки</p>
        </div>
      ) : (
        <div className="documents-grid">
          {documents.map((doc) => (
            <DocumentItem
              key={doc.id}
              document={doc}
              onDownload={handleDownload}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentList;
