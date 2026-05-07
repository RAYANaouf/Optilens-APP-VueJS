const DB_NAME = 'optilens_pos_db';
const DB_VERSION = 1;

const openDB = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('orders')) {
        db.createObjectStore('orders', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('master_data')) {
        db.createObjectStore('master_data');
      }
    };

    request.onsuccess = (event) => resolve(event.target.result);
    request.onerror = (event) => reject(event.target.error);
  });
};

export const ordersDB = {
  async getAll() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('orders', 'readonly');
      const store = transaction.objectStore('orders');
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  },

  async save(order) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('orders', 'readwrite');
      const store = transaction.objectStore('orders');
      const data = JSON.parse(JSON.stringify(order));
      const request = store.put(data);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  },

  async delete(id) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('orders', 'readwrite');
      const store = transaction.objectStore('orders');
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  },

  async clear() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('orders', 'readwrite');
      const store = transaction.objectStore('orders');
      const request = store.clear();
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }
};

export const cacheDB = {
  async get(key) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('master_data', 'readonly');
      const store = transaction.objectStore('master_data');
      const request = store.get(key);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  },

  async set(key, value) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('master_data', 'readwrite');
      const store = transaction.objectStore('master_data');
      const request = store.put(value, key);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }
};
