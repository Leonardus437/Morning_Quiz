// PATCH: Replace line 155-157 in api.js with this:

    // Critical endpoints that must execute immediately
    const isCritical = endpoint.includes('/broadcast') || endpoint.includes('/auth') || endpoint.includes('/health') || endpoint.includes('/admin') || endpoint.includes('/teacher-lessons') || endpoint.includes('/announcements') || endpoint.includes('/schedules');
