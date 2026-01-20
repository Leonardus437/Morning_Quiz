import { writable } from 'svelte/store';

function createNotificationStore() {
  const { subscribe, update } = writable([]);
  
  return {
    subscribe,
    add: (notification) => {
      const id = Date.now() + Math.random();
      const newNotification = {
        id,
        ...notification,
        time: new Date().toLocaleTimeString()
      };
      
      update(notifications => [newNotification, ...notifications]);
      
      setTimeout(() => {
        update(notifications => notifications.filter(n => n.id !== id));
      }, 5000);
    },
    remove: (id) => {
      update(notifications => notifications.filter(n => n.id !== id));
    },
    clear: () => {
      update(() => []);
    }
  };
}

export const notificationStore = createNotificationStore();
