import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Menu,
  Moon,
  Sun,
  BarChart3,
  Upload,
  MessageSquare,
  FileText,
  Settings,
  LogOut,
  Database } from
'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const [isDark, setIsDark] = useState(true);
  const [activeView, setActiveView] = useState('dashboard');

  React.useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);

  if (!user) {
    return <>{children}</>;
  }

  const navigationItems = [
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
  { id: 'upload', label: 'Upload Data', icon: Upload },
  { id: 'chat', label: 'InsightIQ AI', icon: MessageSquare },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'metabase', label: 'Analytics', icon: Database }];


  const Sidebar = ({ isMobile = false }) =>
  <div className={`${isMobile ? 'w-full' : 'w-64'} h-full bg-background border-r flex flex-col`} data-id="xlfs38hna" data-path="src/components/Layout.tsx">
      {/* Header */}
      <div className="p-6 border-b" data-id="cu9m28fiu" data-path="src/components/Layout.tsx">
        <div className="flex items-center space-x-3" data-id="urb42kghy" data-path="src/components/Layout.tsx">
          <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center" data-id="u1wnx4z9t" data-path="src/components/Layout.tsx">
            <BarChart3 className="w-6 h-6 text-primary-foreground" data-id="ofzou2z91" data-path="src/components/Layout.tsx" />
          </div>
          <div data-id="xat3ujsra" data-path="src/components/Layout.tsx">
            <h1 className="text-xl font-bold" data-id="ohgrg7a57" data-path="src/components/Layout.tsx">InsightIQ</h1>
            <p className="text-sm text-muted-foreground" data-id="8t63pnz8k" data-path="src/components/Layout.tsx">BI Platform</p>
          </div>
        </div>
      </div>

      {/* User Info */}
      <div className="p-4 border-b" data-id="3ggn1b430" data-path="src/components/Layout.tsx">
        <div className="flex items-center space-x-3" data-id="m9d5itc45" data-path="src/components/Layout.tsx">
          <Avatar data-id="8uixjiqr3" data-path="src/components/Layout.tsx">
            <AvatarFallback data-id="fzzwbc8dn" data-path="src/components/Layout.tsx">{user.name.charAt(0).toUpperCase()}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0" data-id="b3voimkcs" data-path="src/components/Layout.tsx">
            <p className="text-sm font-medium truncate" data-id="4buj8fk0e" data-path="src/components/Layout.tsx">{user.name}</p>
            <p className="text-xs text-muted-foreground" data-id="vt8o64l55" data-path="src/components/Layout.tsx">ID: {user.user_id}</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2" data-id="tk2beqzbm" data-path="src/components/Layout.tsx">
        {navigationItems.map((item) => {
        const Icon = item.icon;
        return (
          <Button
            key={item.id}
            variant={activeView === item.id ? 'secondary' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setActiveView(item.id)} data-id="fg9a660ag" data-path="src/components/Layout.tsx">

              <Icon className="w-4 h-4 mr-3" data-id="k23r5q08p" data-path="src/components/Layout.tsx" />
              {item.label}
            </Button>);

      })}
      </nav>

      {/* Bottom Actions */}
      <div className="p-4 border-t space-y-2" data-id="iydyy169t" data-path="src/components/Layout.tsx">
        <Button
        variant="ghost"
        size="sm"
        className="w-full justify-start"
        onClick={() => setIsDark(!isDark)} data-id="cx99cf27w" data-path="src/components/Layout.tsx">

          {isDark ? <Sun className="w-4 h-4 mr-3" data-id="myf6avss5" data-path="src/components/Layout.tsx" /> : <Moon className="w-4 h-4 mr-3" data-id="g797gy7bf" data-path="src/components/Layout.tsx" />}
          {isDark ? 'Light Mode' : 'Dark Mode'}
        </Button>
        <Button
        variant="ghost"
        size="sm"
        className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
        onClick={logout} data-id="klt6ksni2" data-path="src/components/Layout.tsx">

          <LogOut className="w-4 h-4 mr-3" data-id="c4qbxco1y" data-path="src/components/Layout.tsx" />
          Logout
        </Button>
      </div>
    </div>;


  return (
    <div className="h-screen flex bg-background" data-id="3mw3ateeq" data-path="src/components/Layout.tsx">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex" data-id="7wcyjtkoa" data-path="src/components/Layout.tsx">
        <Sidebar data-id="nk0n2rgr9" data-path="src/components/Layout.tsx" />
      </div>

      {/* Mobile Sidebar */}
      <Sheet data-id="cai7zaxk2" data-path="src/components/Layout.tsx">
        <SheetTrigger asChild data-id="3k96nn75c" data-path="src/components/Layout.tsx">
          <Button variant="ghost" size="icon" className="md:hidden fixed top-4 left-4 z-50" data-id="jbbnxi3wi" data-path="src/components/Layout.tsx">
            <Menu className="w-5 h-5" data-id="cmxlqvv34" data-path="src/components/Layout.tsx" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="p-0 w-64" data-id="7lu1ngxso" data-path="src/components/Layout.tsx">
          <Sidebar isMobile data-id="mgynvdgdu" data-path="src/components/Layout.tsx" />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden" data-id="gwdt1zx86" data-path="src/components/Layout.tsx">
        <main className="flex-1 overflow-auto" data-id="nyxd0wimb" data-path="src/components/Layout.tsx">
          {React.cloneElement(children as React.ReactElement, { activeView, setActiveView })}
        </main>
      </div>
    </div>);

};

export default Layout;