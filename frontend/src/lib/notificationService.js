import { notificationStore } from './notificationStore.js';
import { api } from './api.js';

let pollingInterval = null;
let lastNotificationId = 0;

export function startNotificationPolling(userRole) {
  if (pollingInterval) {
    clearInterval(pollingInterval);
  }
  
  pollingInterval = setInterval(async () => {
    try {
      const notifications = await api.getNotifications();
      
      // Find new notifications
      const newNotifications = notifications.filter(n => n.id > lastNotificationId && !n.is_read);
      
      if (newNotifications.length > 0) {
        // Update last ID
        lastNotificationId = Math.max(...notifications.map(n => n.id));
        
        // Show toast for each new notification
        newNotifications.forEach(notification => {
          notificationStore.add({
            type: notification.type,
            title: notification.title,
            message: notification.message
          });
        });
      }
    } catch (err) {
      console.error('Notification polling error:', err);
    }
  }, 5000); // Poll every 5 seconds
}

export function stopNotificationPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
}
