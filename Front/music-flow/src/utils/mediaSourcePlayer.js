let currentSession = null;

// Размер буфера в байтах (оптимально для стриминга)
const BUFFER_CHUNK_SIZE = 256 * 1024; // 256KB chunks для быстрой начальной загрузки

export async function loadWithMediaSource(audioElement, url) {
  // Проверка поддержки MediaSource
  if (!window.MediaSource || !MediaSource.isTypeSupported('audio/mpeg')) {
    // Fallback для браузеров без поддержки MediaSource
    audioElement.src = url;
    await audioElement.load();
    return;
  }

  // Отменяем предыдущую загрузку
  if (currentSession) {
    currentSession.abort();
    currentSession = null;
  }

  const session = {
    aborted: false,
    abortController: new AbortController(),
    mediaSource: new MediaSource(),
    objectUrl: null,
    sourceBuffer: null,

    abort() {
      this.aborted = true;
      this.abortController.abort();
      try {
        if (this.sourceBuffer && this.mediaSource.readyState === 'open') {
          this.mediaSource.removeSourceBuffer(this.sourceBuffer);
        }
        if (this.mediaSource.readyState === 'open') {
          this.mediaSource.endOfStream();
        }
      } catch (e) {
        // Игнорируем ошибки при очистке
      }
      if (this.objectUrl) {
        URL.revokeObjectURL(this.objectUrl);
      }
    }
  };

  currentSession = session;
  session.objectUrl = URL.createObjectURL(session.mediaSource);
  audioElement.src = session.objectUrl;

  return new Promise((resolve, reject) => {
    const onError = (error) => {
      if (session.aborted) return;
      session.abort();
      reject(error);
    };

    session.mediaSource.addEventListener('sourceopen', async () => {
      if (session.aborted) return;

      try {
        session.sourceBuffer = session.mediaSource.addSourceBuffer('audio/mpeg');
        session.sourceBuffer.mode = 'sequence';

        let queue = [];
        let updating = false;
        let readingEnded = false;
        let firstChunkLoaded = false;

        const checkEnd = () => {
          if (readingEnded && !updating && queue.length === 0 && session.mediaSource.readyState === 'open') {
            try {
              session.mediaSource.endOfStream();
            } catch (e) {
              // Игнорируем ошибки endOfStream
            }
            resolve();
          }
        };

        const appendChunk = (chunk) => {
          if (session.aborted) return;

          if (!updating && session.mediaSource.readyState === 'open') {
            try {
              updating = true;
              session.sourceBuffer.appendBuffer(chunk);
            } catch (e) {
              onError(e);
            }
          } else {
            queue.push(chunk);
          }
        };

        session.sourceBuffer.addEventListener('updateend', () => {
          if (session.aborted) return;

          updating = false;
          
          // Резолвим после первого чанка для быстрого старта воспроизведения
          if (!firstChunkLoaded) {
            firstChunkLoaded = true;
          }
          
          if (queue.length > 0) {
            appendChunk(queue.shift());
          } else {
            checkEnd();
          }
        });

        session.sourceBuffer.addEventListener('error', () => {
          onError(new Error('SourceBuffer error'));
        });

        const response = await fetch(url, {
          signal: session.abortController.signal,
          headers: {
            'Accept': 'audio/mpeg, audio/*',
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }

        const reader = response.body.getReader();

        const readChunks = async () => {
          try {
            const { done, value } = await reader.read();
            if (session.aborted) return;

            if (done) {
              readingEnded = true;
              checkEnd();
              return;
            }

            appendChunk(value);
            
            // Продолжаем чтение без ожидания
            readChunks();
          } catch (e) {
            if (!session.aborted && e.name !== 'AbortError') {
              onError(e);
            }
          }
        };

        readChunks();
      } catch (e) {
        onError(e);
      }
    });

    session.mediaSource.addEventListener('sourceclose', () => {
      if (!session.aborted) {
        // MediaSource закрыт - это нормально после endOfStream
      }
    });

    audioElement.addEventListener('error', () => {
      if (!session.aborted) {
        onError(new Error('Audio element error'));
      }
    }, { once: true });

    audioElement.load();
  });
}

// Функция для предзагрузки следующего трека
export function preloadTrack(url) {
  return fetch(url, {
    method: 'GET',
    headers: {
      'Accept': 'audio/mpeg, audio/*',
    }
  }).then(response => {
    if (!response.ok) {
      throw new Error(`Preload failed: ${response.status}`);
    }
    return response;
  }).catch(e => {
    console.warn('Preload failed:', e);
  });
}
