# ACE 2.4 Frontend - Deepfake Detection Interface

Modern Next.js frontend for ACE 2.4 deepfake detection system with stunning animations and glassmorphism design.

## Features

- ✨ Fast anime-style animations (Framer Motion)
- 🎨 Glassmorphism UI with neon accents
- 📱 Fully responsive design
- 🔄 Scroll-triggered animations
- 📊 Real-time analysis results
- 🎯 Drag & drop file upload

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **UI**: Custom glassmorphism components
- **Icons**: Lucide React

## Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Docker

```bash
# Build image
docker build -t ace24-frontend .

# Run container
docker run -p 3000:3000 ace24-frontend
```

## Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:
```bash
NEXT_PUBLIC_API_URL=https://your-backend-api.herokuapp.com
```

## Project Structure

```
ace-frontend/
├── app/
│   ├── page.tsx         # Main landing page
│   └── layout.tsx       # Root layout
├── components/
│   ├── about/           # Profile sections
│   ├── upload/          # File upload with analyze
│   ├── results/         # Result cards
│   ├── metrics/         # Performance metrics
│   └── effects/         # Background effects
├── lib/
│   └── api.ts           # Backend API client
├── hooks/               # Custom React hooks
└── public/              # Static assets
```

## Key Components

### Upload Flow
1. Drag & drop or browse files
2. Click "Analyze" button
3. Real-time progress tracking
4. Inline results display

### Animations
- **Title Reveal**: 3-phase glitch effect (0.6s)
- **Profile**: Staggered elements (1.3s total)
- **Scroll Triggered**: All animations retrigger on scroll

### Design System
- **Colors**: Dark theme + neon green/cyan
- **Glass**: Backdrop blur with transparency
- **Typography**: Inter font family
- **Spacing**: Consistent 8px grid

## Deployment

### Cloudflare Pages

1. Push to GitHub
2. Connect to Cloudflare Pages
3. Configure build:
   - Build command: `npm run build`
   - Output directory: `.next`
4. Add environment variables
5. Deploy!

### Vercel (Alternative)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

## Performance

- ⚡ Optimized bundle size
- 🎯 Code splitting
- 📦 Standalone output mode
- 🖼️ Optimized images

## Links

- LinkedIn: [Anyash Prasad](https://www.linkedin.com/in/anyash-prasad-03699a284/)
- Email: anyashprasad.work@gmail.com
- Portfolio: [WikiScan](https://www.wikiscan.dev)

## Contributing

Built with ❤️ by Anyash Prasad

## License

MIT
