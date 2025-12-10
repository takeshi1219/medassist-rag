/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Only use standalone for Docker, Vercel handles this automatically
  ...(process.env.DOCKER_BUILD === 'true' ? { output: 'standalone' } : {}),
  
  // Environment variables available at build time
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  
  // API proxy to backend (works in development and self-hosted)
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // In production on Vercel, don't rewrite - use direct API calls
    if (process.env.VERCEL === '1') {
      return [];
    }
    
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
  
  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },
  
  // Image optimization
  images: {
    domains: [],
    unoptimized: process.env.VERCEL !== '1', // Only optimize on Vercel
  },
};

module.exports = nextConfig;
