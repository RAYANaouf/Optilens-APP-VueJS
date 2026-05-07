const DB_NAME = 'optilens_pos_db3';
const DB_VERSION = 12; // Bump version for robust boolean indexing

const openDB = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      let orderStore;
      if (!db.objectStoreNames.contains('POS Invoice')) {
        orderStore = db.createObjectStore('POS Invoice', { keyPath: 'id' });
      } else {
        orderStore = event.target.transaction.objectStore('POS Invoice');
      }
      
      // Recreate index if it exists to be safe
      if (orderStore.indexNames.contains('to_sync')) {
        orderStore.deleteIndex('to_sync');
      }
      orderStore.createIndex('to_sync', 'to_sync');

      if (!db.objectStoreNames.contains('master_data')) {
        db.createObjectStore('master_data');
      }
    };

    request.onsuccess = (event) => resolve(event.target.result);
    request.onerror = (event) => reject(event.target.error);
  });
};

export const pos_invoice_DB = {
  async getAll() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('POS Invoice', 'readonly');
      const store = transaction.objectStore('POS Invoice');
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  },

  async save(pos_invoice) {
    console.log('📝 Attempting to save POS Invoice:', pos_invoice);
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('POS Invoice', 'readwrite');
      const store = transaction.objectStore('POS Invoice');
      
      // Ensure to_sync is stored as a number (1 for true) for better indexing compatibility
      const data = JSON.parse(JSON.stringify(pos_invoice));
      data.to_sync = data.to_sync ? 1 : 0;
      
      console.log('💾 Saving processed data to IndexedDB:', data);
      
      const request = store.put(data);
      request.onsuccess = () => {
        console.log('✅ Invoice saved successfully to IndexedDB');
        resolve(request.result);
      };
      request.onerror = () => {
        console.error('❌ Error saving invoice to IndexedDB:', request.error);
        reject(request.error);
      };
    });
  },

  async delete(id) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('POS Invoice', 'readwrite');
      const store = transaction.objectStore('POS Invoice');
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  },

  async clear() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('POS Invoice', 'readwrite');
      const store = transaction.objectStore('POS Invoice');
      const request = store.clear();
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  },

  async getToSync() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('POS Invoice', 'readonly');
      const store = transaction.objectStore('POS Invoice');
      const index = store.index('to_sync');
      
      // Query for 1 (which represents true)
      const request = index.getAll(1);
      request.onsuccess = () => resolve(request.result);
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
