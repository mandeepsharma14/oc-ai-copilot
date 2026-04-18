/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
  },
  env: {
    NEXT_PUBLIC_API_URL:       process.env.NEXT_PUBLIC_API_URL       || "http://localhost:8000",
    NEXT_PUBLIC_AZURE_CLIENT_ID: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID || "",
    NEXT_PUBLIC_AZURE_TENANT_ID: process.env.NEXT_PUBLIC_AZURE_TENANT_ID || "",
  },
};

module.exports = nextConfig;
