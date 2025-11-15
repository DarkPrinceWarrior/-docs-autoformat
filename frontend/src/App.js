import React from 'react';
import './App.css';
import FileUploader from './components/FileUploader';
import DocumentList from './components/DocumentList';

function App() {
  const [refreshKey, setRefreshKey] = React.useState(0);

  const handleUploadSuccess = () => {
    // Обновляем список документов после успешной загрузки
    setRefreshKey(prevKey => prevKey + 1);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Форматирование документов по ГОСТ</h1>
        <p>Автоматическое применение требований ГОСТ 7.32-2017 к вашим документам</p>
      </header>

      <main className="App-main">
        <FileUploader onUploadSuccess={handleUploadSuccess} />
        <DocumentList key={refreshKey} />
      </main>

      <footer className="App-footer">
        <p>Powered by Claude AI | ГОСТ 7.32-2017 | FastAPI + React</p>
      </footer>
    </div>
  );
}

export default App;
