import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AuthScreen from '@/components/AuthScreen';
import Layout from '@/components/Layout';
import Dashboard from '@/components/Dashboard';

const HomePage: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center" data-id="8fb2bfic9" data-path="src/pages/HomePage.tsx">
        <div className="text-center space-y-4" data-id="9uuqdvf11" data-path="src/pages/HomePage.tsx">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" data-id="iq4adg0fa" data-path="src/pages/HomePage.tsx" />
          <p className="text-muted-foreground" data-id="gwigmk200" data-path="src/pages/HomePage.tsx">Loading InsightIQ...</p>
        </div>
      </div>);

  }

  if (!user) {
    return <AuthScreen data-id="t3bx5jxps" data-path="src/pages/HomePage.tsx" />;
  }

  return (
    <Layout data-id="by3ya3cu3" data-path="src/pages/HomePage.tsx">
      <Dashboard activeView="dashboard" setActiveView={() => {}} data-id="d1lf6brv4" data-path="src/pages/HomePage.tsx" />
    </Layout>);

};

export default HomePage;