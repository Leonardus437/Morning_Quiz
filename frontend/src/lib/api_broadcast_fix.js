// BROADCAST FIX - Replace lines 155-157 in api.js
// OLD CODE:
//    const criticalEndpoints = ['/auth/login', '/auth/register', '/auth/test', '/health', '/lessons', '/admin/', '/teacher-lessons', '/announcements', '/schedules', '/broadcast', '/quizzes'];
//    const isCritical = criticalEndpoints.some(critical => endpoint.includes(critical)) || endpoint === '/lessons' || method === 'POST' && endpoint.startsWith('/lessons');

// NEW CODE:
    const isCritical = endpoint.includes('/broadcast') || endpoint.includes('/auth') || endpoint.includes('/health') || endpoint.includes('/admin') || endpoint.includes('/teacher-lessons') || endpoint.includes('/announcements') || endpoint.includes('/schedules');
