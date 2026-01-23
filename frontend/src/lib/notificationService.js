import { notificationStore } from './notificationStore.js';
import { api } from './api.js';

let pollingInterval = null;
let lastNotificationId = 0;
let seenNotificationIds = new Set();
let isPolling = false;

// Play notification sound
function playNotificationSound() {
  try {
    // Create a simple beep sound using Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  } catch (err) {
    console.log('Audio notification not available:', err);
  }
}

export function startNotificationPolling(userRole) {
  if (pollingInterval) {
    clearInterval(pollingInterval);
  }
  
  isPolling = true;
  console.log('🔔 Starting real-time notification polling for', userRole);
  
  // Initialize seen notifications on first load
  api.getNotifications().then(notifications => {
    notifications.forEach(n => {
      seenNotificationIds.add(n.id);
      if (n.id > lastNotificationId) {
        lastNotificationId = n.id;
      }
    });
    console.log('🔔 Initialized with', seenNotificationIds.size, 'existing notifications');
  }).catch(err => {
    console.error('Failed to initialize notifications:', err);
  });
  
  // Poll every 3 seconds for real-time updates
  pollingInterval = setInterval(async () => {
    if (!isPolling) return;
    
    try {
      const notifications = await api.getNotifications();
      
      // Find truly NEW notifications (not seen before AND unread)
      const newNotifications = notifications.filter(n => 
        !seenNotificationIds.has(n.id) && !n.is_read
      );
      
      if (newNotifications.length > 0) {
        console.log('🔔 NEW notifications received:', newNotifications.length);
        
        // Update tracking
        newNotifications.forEach(n => {
          seenNotificationIds.add(n.id);
          if (n.id > lastNotificationId) {
            lastNotificationId = n.id;
          }
        });
        
        // Play sound for new notifications
        playNotificationSound();
        
        // Show toast for each new notification
        newNotifications.forEach(notification => {
          console.log('🔔 Showing notification:', notification.title);
          notificationStore.add({
            type: notification.type,
            title: notification.title,
            message: notification.message,
            timestamp: notification.created_at
          });
        });
        
        // Show browser notification if permission granted
        if ('Notification' in window && Notification.permission === 'granted') {
          newNotifications.forEach(notification => {
            new Notification(notification.title, {
              body: notification.message,
              icon: '/icon-192.png',
              badge: '/icon-192.png'
            });
          });
        }
      }
    } catch (err) {
      console.error('Notification polling error:', err);
    }
  }, 3000); // Poll every 3 seconds for real-time feel
}

export function stopNotificationPolling() {
  isPolling = false;
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
  console.log('🔔 Stopped notification polling');
}

// Request browser notification permission
export function requestNotificationPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission().then(permission => {
      console.log('Notification permission:', permission);
    });
  }
}
