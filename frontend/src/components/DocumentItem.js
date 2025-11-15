import React from 'react';
import './DocumentItem.css';

const DocumentItem = ({ document, onDownload }) => {
  const getStatusInfo = (status) => {
    switch (status) {
      case 'uploaded':
        return { text: 'Загружен', color: '#60a5fa', icon: '📄' };
      case 'processing':
        return { text: 'Обработка...', color: '#fbbf24', icon: '⚙️' };
      case 'completed':
        return { text: 'Готов', color: '#4ade80', icon: '✓' };
      case 'failed':
        return { text: 'Ошибка', color: '#ef4444', icon: '✗' };
      default:
        return { text: status, color: '#9ca3af', icon: '?' };
    }
  };

  const statusInfo = getStatusInfo(document.status);
  const createdDate = new Date(document.created_at).toLocaleString('ru-RU');

  return (
    <div className="document-item">
      <div className="document-header">
        <div className="document-icon">📝</div>
        <div className="document-info">
          <h3 className="document-title" title={document.original_filename}>
            {document.original_filename}
          </h3>
          <p className="document-date">{createdDate}</p>
        </div>
      </div>

      <div className="document-body">
        <div className="status-badge" style={{ background: statusInfo.color }}>
          <span className="status-icon">{statusInfo.icon}</span>
          <span className="status-text">{statusInfo.text}</span>
        </div>

        {document.status === 'processing' && (
          <div className="progress-bar">
            <div className="progress-bar-fill"></div>
          </div>
        )}

        {document.status === 'failed' && document.error_message && (
          <div className="error-details">
            <p className="error-label">Ошибка:</p>
            <p className="error-text">{document.error_message}</p>
          </div>
        )}

        {document.status === 'completed' && (
          <button
            className="download-button"
            onClick={() => onDownload(document.id, document.original_filename)}
          >
            <svg
              className="download-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Скачать отформатированный документ
          </button>
        )}
      </div>
    </div>
  );
};

export default DocumentItem;
