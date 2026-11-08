/** @type {import('next').NextConfig} */
const nextConfig = {
  images: { remotePatterns: [], formats: ['image/avif', 'image/webp'] },
  experimental: { optimizePackageImports: ['lucide-react'] },
  transpilePackages: [],
};

module.exports = nextConfig;
