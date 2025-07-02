import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import FileUpload from '@/components/FileUpload';
import AIChat from '@/components/AIChat';
import ReportsView from '@/components/ReportsView';
import MetabaseEmbed from '@/components/MetabaseEmbed';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { supabase } from '@/lib/supabase';
import {
  FileText,
  Database,
  TrendingUp,
  Users,
  RefreshCw,
  MoreHorizontal } from
'lucide-react';

interface DashboardProps {
  activeView: string;
  setActiveView: (view: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ activeView, setActiveView }) => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalFiles: 0,
    recentUploads: 0,
    analysisComplete: 0,
    totalSize: 0
  });
  const [recentFiles, setRecentFiles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadDashboardData();
    }
  }, [user]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Get user's file uploads
      const { data: files, error } = await supabase.
      from('file_uploads').
      select('*').
      eq('user_id', user?.user_id).
      order('upload_timestamp', { ascending: false });

      if (error) {
        console.error('Error loading files:', error);
        return;
      }

      const totalFiles = files?.length || 0;
      const recentUploads = files?.filter((f) =>
      new Date(f.upload_timestamp) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      ).length || 0;
      const analysisComplete = files?.filter((f) => f.analysis_results).length || 0;
      const totalSize = files?.reduce((sum, f) => sum + (f.file_size || 0), 0) || 0;

      setStats({
        totalFiles,
        recentUploads,
        analysisComplete,
        totalSize
      });

      setRecentFiles(files?.slice(0, 5) || []);
    } catch (error) {
      console.error('Dashboard data loading error:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (activeView === 'upload') {
    return <FileUpload onUploadComplete={loadDashboardData} data-id="9cxwil96a" data-path="src/components/Dashboard.tsx" />;
  }

  if (activeView === 'chat') {
    return <AIChat data-id="bxsk8dplf" data-path="src/components/Dashboard.tsx" />;
  }

  if (activeView === 'reports') {
    return <ReportsView data-id="qa7on3uhf" data-path="src/components/Dashboard.tsx" />;
  }

  if (activeView === 'metabase') {
    return <MetabaseEmbed data-id="w6df192fi" data-path="src/components/Dashboard.tsx" />;
  }

  return (
    <div className="p-6 space-y-6" data-id="289yt1sf8" data-path="src/components/Dashboard.tsx">
      {/* Welcome Header */}
      <div className="flex items-center justify-between" data-id="8gxx3zmyw" data-path="src/components/Dashboard.tsx">
        <div data-id="v0jagj4hv" data-path="src/components/Dashboard.tsx">
          <h1 className="text-3xl font-bold" data-id="7rqcgl197" data-path="src/components/Dashboard.tsx">Welcome back, {user?.name}!</h1>
          <p className="text-muted-foreground mt-1" data-id="2n4l8topt" data-path="src/components/Dashboard.tsx">
            Here's your business intelligence overview
          </p>
        </div>
        <Button onClick={loadDashboardData} disabled={loading} data-id="9gue3o7n4" data-path="src/components/Dashboard.tsx">
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} data-id="nbqov4nh0" data-path="src/components/Dashboard.tsx" />
          Refresh
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" data-id="zm4tcpjs7" data-path="src/components/Dashboard.tsx">
        <Card data-id="fnqyah6at" data-path="src/components/Dashboard.tsx">
          <CardContent className="p-6" data-id="e8d94wi8r" data-path="src/components/Dashboard.tsx">
            <div className="flex items-center justify-between" data-id="264fecgma" data-path="src/components/Dashboard.tsx">
              <div data-id="041vt1frp" data-path="src/components/Dashboard.tsx">
                <p className="text-sm font-medium text-muted-foreground" data-id="qnpvzkbw2" data-path="src/components/Dashboard.tsx">Total Files</p>
                <p className="text-2xl font-bold" data-id="j7h3zogs3" data-path="src/components/Dashboard.tsx">{stats.totalFiles}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-600" data-id="t8a356fal" data-path="src/components/Dashboard.tsx" />
            </div>
          </CardContent>
        </Card>

        <Card data-id="86dr7d8q9" data-path="src/components/Dashboard.tsx">
          <CardContent className="p-6" data-id="7nxehfmwl" data-path="src/components/Dashboard.tsx">
            <div className="flex items-center justify-between" data-id="wah078lvv" data-path="src/components/Dashboard.tsx">
              <div data-id="ocl388sfg" data-path="src/components/Dashboard.tsx">
                <p className="text-sm font-medium text-muted-foreground" data-id="lr3m8sp5v" data-path="src/components/Dashboard.tsx">Recent Uploads</p>
                <p className="text-2xl font-bold" data-id="7d37ow6xc" data-path="src/components/Dashboard.tsx">{stats.recentUploads}</p>
                <p className="text-xs text-muted-foreground" data-id="83d0lyddn" data-path="src/components/Dashboard.tsx">Last 7 days</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" data-id="2wok8j4do" data-path="src/components/Dashboard.tsx" />
            </div>
          </CardContent>
        </Card>

        <Card data-id="syqyzpdxv" data-path="src/components/Dashboard.tsx">
          <CardContent className="p-6" data-id="sdx1s29to" data-path="src/components/Dashboard.tsx">
            <div className="flex items-center justify-between" data-id="dzo7igy9w" data-path="src/components/Dashboard.tsx">
              <div data-id="4zjfy2p1m" data-path="src/components/Dashboard.tsx">
                <p className="text-sm font-medium text-muted-foreground" data-id="1nn71jpsh" data-path="src/components/Dashboard.tsx">AI Analysis</p>
                <p className="text-2xl font-bold" data-id="dmxpveqfa" data-path="src/components/Dashboard.tsx">{stats.analysisComplete}</p>
                <p className="text-xs text-muted-foreground" data-id="jjr0hit8p" data-path="src/components/Dashboard.tsx">Completed</p>
              </div>
              <Database className="w-8 h-8 text-purple-600" data-id="o6y77qeov" data-path="src/components/Dashboard.tsx" />
            </div>
          </CardContent>
        </Card>

        <Card data-id="bfu7aepsr" data-path="src/components/Dashboard.tsx">
          <CardContent className="p-6" data-id="prqajpsmi" data-path="src/components/Dashboard.tsx">
            <div className="flex items-center justify-between" data-id="ded9mx083" data-path="src/components/Dashboard.tsx">
              <div data-id="kaziebeh9" data-path="src/components/Dashboard.tsx">
                <p className="text-sm font-medium text-muted-foreground" data-id="eke4g8g6h" data-path="src/components/Dashboard.tsx">Storage Used</p>
                <p className="text-2xl font-bold" data-id="b4ju8ovba" data-path="src/components/Dashboard.tsx">{formatFileSize(stats.totalSize)}</p>
              </div>
              <Users className="w-8 h-8 text-orange-600" data-id="iuvnvgjnz" data-path="src/components/Dashboard.tsx" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Files */}
      <Card data-id="gs6paz2k5" data-path="src/components/Dashboard.tsx">
        <CardHeader data-id="kxobjqpar" data-path="src/components/Dashboard.tsx">
          <CardTitle data-id="mbcwzn9u6" data-path="src/components/Dashboard.tsx">Recent Files</CardTitle>
        </CardHeader>
        <CardContent data-id="f03zyyxjj" data-path="src/components/Dashboard.tsx">
          {recentFiles.length === 0 ?
          <div className="text-center py-8" data-id="vzjuh1q5r" data-path="src/components/Dashboard.tsx">
              <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" data-id="fnzze731y" data-path="src/components/Dashboard.tsx" />
              <p className="text-lg font-medium" data-id="5autb8iat" data-path="src/components/Dashboard.tsx">No files uploaded yet</p>
              <p className="text-muted-foreground mb-4" data-id="pk7a327lo" data-path="src/components/Dashboard.tsx">
                Start by uploading your first dataset to begin analysis
              </p>
              <Button onClick={() => setActiveView('upload')} data-id="zpksg84mp" data-path="src/components/Dashboard.tsx">
                Upload Data
              </Button>
            </div> :

          <div className="space-y-4" data-id="pw155xr7n" data-path="src/components/Dashboard.tsx">
              {recentFiles.map((file) =>
            <div key={file.id} className="flex items-center justify-between p-4 border rounded-lg" data-id="rbe75tc7o" data-path="src/components/Dashboard.tsx">
                  <div className="flex items-center space-x-4" data-id="scm47912v" data-path="src/components/Dashboard.tsx">
                    <div className="w-10 h-10 rounded bg-primary/10 flex items-center justify-center" data-id="63l2lkzth" data-path="src/components/Dashboard.tsx">
                      <FileText className="w-5 h-5 text-primary" data-id="5eisw4jw0" data-path="src/components/Dashboard.tsx" />
                    </div>
                    <div data-id="xpzc36vr0" data-path="src/components/Dashboard.tsx">
                      <p className="font-medium" data-id="5oa1dk8f3" data-path="src/components/Dashboard.tsx">{file.file_name}</p>
                      <p className="text-sm text-muted-foreground" data-id="84fzo7rwe" data-path="src/components/Dashboard.tsx">
                        {formatFileSize(file.file_size)} • {formatDate(file.upload_timestamp)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2" data-id="mqwg5damk" data-path="src/components/Dashboard.tsx">
                    <Badge variant={file.analysis_results ? 'default' : 'secondary'} data-id="1joxblawh" data-path="src/components/Dashboard.tsx">
                      {file.analysis_results ? 'Analyzed' : 'Pending'}
                    </Badge>
                    <Button variant="ghost" size="icon" data-id="e2xiygwkz" data-path="src/components/Dashboard.tsx">
                      <MoreHorizontal className="w-4 h-4" data-id="56j7bjgan" data-path="src/components/Dashboard.tsx" />
                    </Button>
                  </div>
                </div>
            )}
            </div>
          }
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6" data-id="2tumqt2fl" data-path="src/components/Dashboard.tsx">
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setActiveView('upload')} data-id="0ydsp8rko" data-path="src/components/Dashboard.tsx">
          <CardHeader data-id="y7efr0gx3" data-path="src/components/Dashboard.tsx">
            <CardTitle className="flex items-center space-x-2" data-id="np3xhj1do" data-path="src/components/Dashboard.tsx">
              <FileText className="w-5 h-5" data-id="9dllwdnp8" data-path="src/components/Dashboard.tsx" />
              <span data-id="lbuj3014l" data-path="src/components/Dashboard.tsx">Upload Data</span>
            </CardTitle>
          </CardHeader>
          <CardContent data-id="sh90v1zf7" data-path="src/components/Dashboard.tsx">
            <p className="text-sm text-muted-foreground" data-id="r0gizs4tf" data-path="src/components/Dashboard.tsx">
              Upload CSV, Excel files or connect databases for analysis
            </p>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setActiveView('chat')} data-id="bt53b7a3v" data-path="src/components/Dashboard.tsx">
          <CardHeader data-id="2ptrwas0p" data-path="src/components/Dashboard.tsx">
            <CardTitle className="flex items-center space-x-2" data-id="lfjd5c5sx" data-path="src/components/Dashboard.tsx">
              <Database className="w-5 h-5" data-id="t6pzx9nes" data-path="src/components/Dashboard.tsx" />
              <span data-id="2zv2492c0" data-path="src/components/Dashboard.tsx">Ask InsightIQ</span>
            </CardTitle>
          </CardHeader>
          <CardContent data-id="ujpuai96q" data-path="src/components/Dashboard.tsx">
            <p className="text-sm text-muted-foreground" data-id="3jrfipu3u" data-path="src/components/Dashboard.tsx">
              Chat with AI to get insights and analysis from your data
            </p>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setActiveView('reports')} data-id="9k9nbuz50" data-path="src/components/Dashboard.tsx">
          <CardHeader data-id="ob5xfwwm9" data-path="src/components/Dashboard.tsx">
            <CardTitle className="flex items-center space-x-2" data-id="7aafrn2ok" data-path="src/components/Dashboard.tsx">
              <TrendingUp className="w-5 h-5" data-id="0tehwe2ya" data-path="src/components/Dashboard.tsx" />
              <span data-id="41j5k815y" data-path="src/components/Dashboard.tsx">Generate Reports</span>
            </CardTitle>
          </CardHeader>
          <CardContent data-id="jzon3njjg" data-path="src/components/Dashboard.tsx">
            <p className="text-sm text-muted-foreground" data-id="jp0xmkxs1" data-path="src/components/Dashboard.tsx">
              Create and download comprehensive analysis reports
            </p>
          </CardContent>
        </Card>
      </div>
    </div>);

};

export default Dashboard;