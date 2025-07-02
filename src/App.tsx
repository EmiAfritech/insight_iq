import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from 'next-themes';
import { AuthProvider } from '@/contexts/AuthContext';
import HomePage from './pages/HomePage';
import NotFound from './pages/NotFound';
import { Toaster as SonnerToaster } from 'sonner';

const queryClient = new QueryClient();

const App = () =>
<QueryClientProvider client={queryClient} data-id="gxrmq9izs" data-path="src/App.tsx">
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem data-id="1ihqo1o5r" data-path="src/App.tsx">
      <AuthProvider data-id="1r32pnslr" data-path="src/App.tsx">
        <TooltipProvider data-id="wlliuv961" data-path="src/App.tsx">
          <Toaster data-id="yxghoe7xb" data-path="src/App.tsx" />
          <SonnerToaster richColors position="top-right" data-id="h1b96cx53" data-path="src/App.tsx" />
          <BrowserRouter data-id="oqarm0yue" data-path="src/App.tsx">
            <Routes data-id="dede7d2ea" data-path="src/App.tsx">
              <Route path="/" element={<HomePage data-id="jzihc0x28" data-path="src/App.tsx" />} data-id="tab0qgd7a" data-path="src/App.tsx" />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound data-id="fyr7137je" data-path="src/App.tsx" />} data-id="j2c37g0p5" data-path="src/App.tsx" />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>;


export default App;