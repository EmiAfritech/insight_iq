import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ExternalLink, BarChart3, Database, TrendingUp } from 'lucide-react';

const MetabaseEmbed: React.FC = () => {
  const openMetabase = () => {
    window.open('http://localhost:3000', '_blank');
  };

  return (
    <div className="p-6 space-y-6" data-id="x4g1zcvlx" data-path="src/components/MetabaseEmbed.tsx">
      <div data-id="j096gpk0f" data-path="src/components/MetabaseEmbed.tsx">
        <h1 className="text-3xl font-bold" data-id="roontbb08" data-path="src/components/MetabaseEmbed.tsx">Analytics Dashboard</h1>
        <p className="text-muted-foreground mt-1" data-id="hib2l5wfs" data-path="src/components/MetabaseEmbed.tsx">
          Advanced data visualization and exploration with Metabase
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" data-id="dmlrp7783" data-path="src/components/MetabaseEmbed.tsx">
        {/* Metabase Info */}
        <Card data-id="e64er68a4" data-path="src/components/MetabaseEmbed.tsx">
          <CardHeader data-id="rc82f8gak" data-path="src/components/MetabaseEmbed.tsx">
            <CardTitle className="flex items-center space-x-2" data-id="5o2umbhly" data-path="src/components/MetabaseEmbed.tsx">
              <BarChart3 className="w-5 h-5" data-id="azxy37ou2" data-path="src/components/MetabaseEmbed.tsx" />
              <span data-id="hvjgwgndr" data-path="src/components/MetabaseEmbed.tsx">Metabase Integration</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4" data-id="0b7ptyoe9" data-path="src/components/MetabaseEmbed.tsx">
            <p className="text-sm text-muted-foreground" data-id="08m4hmesy" data-path="src/components/MetabaseEmbed.tsx">
              Metabase provides powerful visualization and dashboard capabilities for your uploaded data.
              Create custom charts, explore trends, and build comprehensive dashboards.
            </p>
            
            <div className="space-y-3" data-id="6ymoe3zmf" data-path="src/components/MetabaseEmbed.tsx">
              <div className="flex items-start space-x-3" data-id="qkh8tm3lf" data-path="src/components/MetabaseEmbed.tsx">
                <Database className="w-5 h-5 text-blue-600 mt-0.5" data-id="mi1s3vp5d" data-path="src/components/MetabaseEmbed.tsx" />
                <div data-id="7niwkqnia" data-path="src/components/MetabaseEmbed.tsx">
                  <p className="font-medium" data-id="trp0b7qbm" data-path="src/components/MetabaseEmbed.tsx">Connected Database</p>
                  <p className="text-sm text-muted-foreground" data-id="hnh0my6vm" data-path="src/components/MetabaseEmbed.tsx">
                    Your Supabase PostgreSQL database is connected to Metabase
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3" data-id="hmneunokc" data-path="src/components/MetabaseEmbed.tsx">
                <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" data-id="r1334yl75" data-path="src/components/MetabaseEmbed.tsx" />
                <div data-id="9uk49jlwi" data-path="src/components/MetabaseEmbed.tsx">
                  <p className="font-medium" data-id="l7fabz75g" data-path="src/components/MetabaseEmbed.tsx">Real-time Analytics</p>
                  <p className="text-sm text-muted-foreground" data-id="k96cpibjn" data-path="src/components/MetabaseEmbed.tsx">
                    Visualize your uploaded data with interactive charts and graphs
                  </p>
                </div>
              </div>
            </div>

            <Button onClick={openMetabase} className="w-full" data-id="txq63wa6e" data-path="src/components/MetabaseEmbed.tsx">
              <ExternalLink className="w-4 h-4 mr-2" data-id="tludhp22j" data-path="src/components/MetabaseEmbed.tsx" />
              Open Metabase Dashboard
            </Button>
          </CardContent>
        </Card>

        {/* Setup Instructions */}
        <Card data-id="96lm3q7tm" data-path="src/components/MetabaseEmbed.tsx">
          <CardHeader data-id="92a3p5zr2" data-path="src/components/MetabaseEmbed.tsx">
            <CardTitle data-id="dca7ioos3" data-path="src/components/MetabaseEmbed.tsx">Setup Instructions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4" data-id="l6pql6ji0" data-path="src/components/MetabaseEmbed.tsx">
            <div className="space-y-3 text-sm" data-id="9fmdccq2w" data-path="src/components/MetabaseEmbed.tsx">
              <div className="p-3 bg-muted rounded-lg" data-id="96rn0bm2x" data-path="src/components/MetabaseEmbed.tsx">
                <p className="font-medium mb-1" data-id="93tmu967m" data-path="src/components/MetabaseEmbed.tsx">1. Access Metabase</p>
                <p className="text-muted-foreground" data-id="6efl2byb9" data-path="src/components/MetabaseEmbed.tsx">
                  Click the button to open Metabase in a new tab
                </p>
              </div>
              
              <div className="p-3 bg-muted rounded-lg" data-id="po3typtr9" data-path="src/components/MetabaseEmbed.tsx">
                <p className="font-medium mb-1" data-id="lr4wqfb0n" data-path="src/components/MetabaseEmbed.tsx">2. Database Connection</p>
                <p className="text-muted-foreground" data-id="uklqdig6b" data-path="src/components/MetabaseEmbed.tsx">
                  Your Supabase database is already configured and connected
                </p>
              </div>
              
              <div className="p-3 bg-muted rounded-lg" data-id="ocm3cvrys" data-path="src/components/MetabaseEmbed.tsx">
                <p className="font-medium mb-1" data-id="x40qqgapu" data-path="src/components/MetabaseEmbed.tsx">3. Create Dashboards</p>
                <p className="text-muted-foreground" data-id="iziw2tuso" data-path="src/components/MetabaseEmbed.tsx">
                  Use the "file_uploads" table to access your uploaded data
                </p>
              </div>
              
              <div className="p-3 bg-muted rounded-lg" data-id="n4jfawp7u" data-path="src/components/MetabaseEmbed.tsx">
                <p className="font-medium mb-1" data-id="7eselathj" data-path="src/components/MetabaseEmbed.tsx">4. Share Insights</p>
                <p className="text-muted-foreground" data-id="32s4fp3if" data-path="src/components/MetabaseEmbed.tsx">
                  Create and share interactive dashboards with your team
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Embedded Frame Placeholder */}
      <Card data-id="wsqzw4dqv" data-path="src/components/MetabaseEmbed.tsx">
        <CardHeader data-id="i41j07mha" data-path="src/components/MetabaseEmbed.tsx">
          <CardTitle data-id="30igwwi3l" data-path="src/components/MetabaseEmbed.tsx">Dashboard Preview</CardTitle>
        </CardHeader>
        <CardContent data-id="kh2blag29" data-path="src/components/MetabaseEmbed.tsx">
          <div className="h-96 bg-muted rounded-lg flex items-center justify-center" data-id="t98ztxrqk" data-path="src/components/MetabaseEmbed.tsx">
            <div className="text-center space-y-4" data-id="6c9b4xe14" data-path="src/components/MetabaseEmbed.tsx">
              <BarChart3 className="w-16 h-16 text-muted-foreground mx-auto" data-id="z0ctwisdf" data-path="src/components/MetabaseEmbed.tsx" />
              <div data-id="1yiifw44e" data-path="src/components/MetabaseEmbed.tsx">
                <p className="text-lg font-medium" data-id="ac3ogjrsw" data-path="src/components/MetabaseEmbed.tsx">Metabase Dashboard</p>
                <p className="text-muted-foreground" data-id="n2hebdwps" data-path="src/components/MetabaseEmbed.tsx">
                  Click "Open Metabase Dashboard" to access the full analytics interface
                </p>
              </div>
              <Button onClick={openMetabase} variant="outline" data-id="ev9d3w7dr" data-path="src/components/MetabaseEmbed.tsx">
                <ExternalLink className="w-4 h-4 mr-2" data-id="1w6902h4c" data-path="src/components/MetabaseEmbed.tsx" />
                Launch Metabase
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>);

};

export default MetabaseEmbed;