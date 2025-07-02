import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { supabase } from '@/lib/supabase';
import { toast } from 'sonner';
import {
  FileText,
  Download,
  Eye,
  Calendar,
  TrendingUp,
  Database,
  CheckCircle,
  Loader2 } from
'lucide-react';
import jsPDF from 'jspdf';

const ReportsView: React.FC = () => {
  const { user } = useAuth();
  const [files, setFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [generating, setGenerating] = useState(false);
  const [reportData, setReportData] = useState<any>(null);

  useEffect(() => {
    loadUserFiles();
  }, [user]);

  const loadUserFiles = async () => {
    try {
      const { data, error } = await supabase.
      from('file_uploads').
      select('*').
      eq('user_id', user?.user_id).
      not('analysis_results', 'is', null).
      order('upload_timestamp', { ascending: false });

      if (error) {
        console.error('Error loading files:', error);
        return;
      }

      setFiles(data || []);
      if (data && data.length > 0 && !selectedFile) {
        setSelectedFile(data[0].id);
        setReportData(data[0].analysis_results);
      }
    } catch (error) {
      console.error('Error loading user files:', error);
    }
  };

  const handleFileSelect = (fileId: string) => {
    setSelectedFile(fileId);
    const file = files.find((f) => f.id === fileId);
    if (file) {
      setReportData(file.analysis_results);
    }
  };

  const generatePDFReport = async () => {
    if (!reportData || !selectedFile) {
      toast.error('Please select a file to generate a report');
      return;
    }

    setGenerating(true);
    try {
      const selectedFileData = files.find((f) => f.id === selectedFile);

      const pdf = new jsPDF();
      const pageWidth = pdf.internal.pageSize.width;
      let yPosition = 20;

      // Header
      pdf.setFontSize(20);
      pdf.setTextColor(40, 40, 40);
      pdf.text('InsightIQ Analysis Report', 20, yPosition);

      yPosition += 10;
      pdf.setFontSize(12);
      pdf.setTextColor(100, 100, 100);
      pdf.text(`Generated on ${new Date().toLocaleDateString()}`, 20, yPosition);

      yPosition += 20;

      // File Information
      pdf.setFontSize(16);
      pdf.setTextColor(40, 40, 40);
      pdf.text('File Information', 20, yPosition);
      yPosition += 10;

      pdf.setFontSize(10);
      pdf.text(`File Name: ${selectedFileData?.file_name}`, 20, yPosition);
      yPosition += 7;
      pdf.text(`Upload Date: ${new Date(selectedFileData?.upload_timestamp).toLocaleDateString()}`, 20, yPosition);
      yPosition += 7;
      pdf.text(`File Size: ${formatFileSize(selectedFileData?.file_size)}`, 20, yPosition);
      yPosition += 15;

      // Data Dictionary
      if (reportData.dataDictionary && Object.keys(reportData.dataDictionary).length > 0) {
        pdf.setFontSize(16);
        pdf.setTextColor(40, 40, 40);
        pdf.text('Data Dictionary', 20, yPosition);
        yPosition += 10;

        pdf.setFontSize(10);
        Object.entries(reportData.dataDictionary).forEach(([key, value]: [string, any]) => {
          if (yPosition > 280) {
            pdf.addPage();
            yPosition = 20;
          }
          pdf.text(`${key}: ${String(value).slice(0, 80)}`, 20, yPosition);
          yPosition += 7;
        });
        yPosition += 10;
      }

      // Validation Rules
      if (reportData.validationRules && Object.keys(reportData.validationRules).length > 0) {
        if (yPosition > 250) {
          pdf.addPage();
          yPosition = 20;
        }

        pdf.setFontSize(16);
        pdf.setTextColor(40, 40, 40);
        pdf.text('Validation Rules', 20, yPosition);
        yPosition += 10;

        pdf.setFontSize(10);
        Object.entries(reportData.validationRules).forEach(([key, value]: [string, any]) => {
          if (yPosition > 280) {
            pdf.addPage();
            yPosition = 20;
          }
          pdf.text(`${key}: ${String(value).slice(0, 80)}`, 20, yPosition);
          yPosition += 7;
        });
        yPosition += 10;
      }

      // Insights
      if (reportData.insights) {
        if (yPosition > 200) {
          pdf.addPage();
          yPosition = 20;
        }

        pdf.setFontSize(16);
        pdf.setTextColor(40, 40, 40);
        pdf.text('Key Insights', 20, yPosition);
        yPosition += 10;

        pdf.setFontSize(10);
        const insightLines = pdf.splitTextToSize(reportData.insights, pageWidth - 40);
        insightLines.forEach((line: string) => {
          if (yPosition > 280) {
            pdf.addPage();
            yPosition = 20;
          }
          pdf.text(line, 20, yPosition);
          yPosition += 7;
        });
        yPosition += 10;
      }

      // Recommendations
      if (reportData.recommendations) {
        if (yPosition > 200) {
          pdf.addPage();
          yPosition = 20;
        }

        pdf.setFontSize(16);
        pdf.setTextColor(40, 40, 40);
        pdf.text('Recommendations', 20, yPosition);
        yPosition += 10;

        pdf.setFontSize(10);
        const recommendationLines = pdf.splitTextToSize(reportData.recommendations, pageWidth - 40);
        recommendationLines.forEach((line: string) => {
          if (yPosition > 280) {
            pdf.addPage();
            yPosition = 20;
          }
          pdf.text(line, 20, yPosition);
          yPosition += 7;
        });
      }

      // Save PDF
      const fileName = `InsightIQ_Report_${selectedFileData?.file_name.replace(/\.[^/.]+$/, '')}_${new Date().toISOString().split('T')[0]}.pdf`;
      pdf.save(fileName);

      toast.success('PDF report generated successfully!');
    } catch (error) {
      console.error('PDF generation error:', error);
      toast.error('Failed to generate PDF report');
    } finally {
      setGenerating(false);
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
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="p-6 space-y-6" data-id="ole5ry3fs" data-path="src/components/ReportsView.tsx">
      <div data-id="vpeqbvdcm" data-path="src/components/ReportsView.tsx">
        <h1 className="text-3xl font-bold" data-id="yzrmzbyca" data-path="src/components/ReportsView.tsx">Reports & Analysis</h1>
        <p className="text-muted-foreground mt-1" data-id="dnyd74wio" data-path="src/components/ReportsView.tsx">
          Generate and download comprehensive analysis reports
        </p>
      </div>

      {files.length === 0 ?
      <Card data-id="l38gszav5" data-path="src/components/ReportsView.tsx">
          <CardContent className="p-12 text-center" data-id="w4dbwugen" data-path="src/components/ReportsView.tsx">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" data-id="cangv81dy" data-path="src/components/ReportsView.tsx" />
            <h3 className="text-lg font-medium mb-2" data-id="je02j9qi4" data-path="src/components/ReportsView.tsx">No analyzed files found</h3>
            <p className="text-muted-foreground mb-4" data-id="nbo22a0mx" data-path="src/components/ReportsView.tsx">
              Upload and analyze files first to generate reports
            </p>
            <Button onClick={() => window.location.hash = '#upload'} data-id="sfgrlwvk3" data-path="src/components/ReportsView.tsx">
              Upload Data
            </Button>
          </CardContent>
        </Card> :

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6" data-id="68yga1e82" data-path="src/components/ReportsView.tsx">
          {/* File Selection */}
          <Card data-id="oo67iv91u" data-path="src/components/ReportsView.tsx">
            <CardHeader data-id="fffraa29n" data-path="src/components/ReportsView.tsx">
              <CardTitle className="flex items-center space-x-2" data-id="dxamomd4s" data-path="src/components/ReportsView.tsx">
                <Database className="w-5 h-5" data-id="q5ezu6o05" data-path="src/components/ReportsView.tsx" />
                <span data-id="qaosa08bt" data-path="src/components/ReportsView.tsx">Select Dataset</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4" data-id="2w6hwfrce" data-path="src/components/ReportsView.tsx">
              <Select value={selectedFile} onValueChange={handleFileSelect} data-id="jwzwa578n" data-path="src/components/ReportsView.tsx">
                <SelectTrigger data-id="mu4fkewds" data-path="src/components/ReportsView.tsx">
                  <SelectValue placeholder="Choose a file" data-id="m9inc94kn" data-path="src/components/ReportsView.tsx" />
                </SelectTrigger>
                <SelectContent data-id="rhxf07suo" data-path="src/components/ReportsView.tsx">
                  {files.map((file) =>
                <SelectItem key={file.id} value={file.id} data-id="5qy5zteog" data-path="src/components/ReportsView.tsx">
                      <div className="flex items-center space-x-2" data-id="es0kkbs1s" data-path="src/components/ReportsView.tsx">
                        <FileText className="w-4 h-4" data-id="oyziq0d74" data-path="src/components/ReportsView.tsx" />
                        <span data-id="rxkv2wl19" data-path="src/components/ReportsView.tsx">{file.file_name}</span>
                      </div>
                    </SelectItem>
                )}
                </SelectContent>
              </Select>

              {selectedFile &&
            <div className="space-y-3" data-id="82qsnf0dq" data-path="src/components/ReportsView.tsx">
                  {files.
              filter((f) => f.id === selectedFile).
              map((file) =>
              <div key={file.id} className="p-3 bg-muted rounded-lg" data-id="vzh2rjq6i" data-path="src/components/ReportsView.tsx">
                        <div className="flex items-center justify-between mb-2" data-id="65ek0s8xs" data-path="src/components/ReportsView.tsx">
                          <h4 className="font-medium" data-id="teksdf9fd" data-path="src/components/ReportsView.tsx">{file.file_name}</h4>
                          <Badge variant="default" data-id="gko1ofgzf" data-path="src/components/ReportsView.tsx">
                            <CheckCircle className="w-3 h-3 mr-1" data-id="jafdas2r9" data-path="src/components/ReportsView.tsx" />
                            Analyzed
                          </Badge>
                        </div>
                        <div className="text-sm text-muted-foreground space-y-1" data-id="ttvq5kjd9" data-path="src/components/ReportsView.tsx">
                          <p data-id="b2gh1vfhh" data-path="src/components/ReportsView.tsx">Size: {formatFileSize(file.file_size)}</p>
                          <p data-id="912jxpbw8" data-path="src/components/ReportsView.tsx">Uploaded: {formatDate(file.upload_timestamp)}</p>
                        </div>
                      </div>
              )}
                </div>
            }

              <div className="space-y-2" data-id="drvgipv93" data-path="src/components/ReportsView.tsx">
                <Button
                onClick={generatePDFReport}
                disabled={!selectedFile || generating}
                className="w-full" data-id="amnz1bkyf" data-path="src/components/ReportsView.tsx">

                  {generating ?
                <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" data-id="l5qx7r5gm" data-path="src/components/ReportsView.tsx" />
                      Generating...
                    </> :

                <>
                      <Download className="w-4 h-4 mr-2" data-id="21czeco0v" data-path="src/components/ReportsView.tsx" />
                      Generate PDF Report
                    </>
                }
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Report Preview */}
          <div className="lg:col-span-2" data-id="lgkjhli89" data-path="src/components/ReportsView.tsx">
            <Card data-id="viwsmh7y9" data-path="src/components/ReportsView.tsx">
              <CardHeader data-id="ksn7ar8zu" data-path="src/components/ReportsView.tsx">
                <CardTitle className="flex items-center space-x-2" data-id="ql5voa2fa" data-path="src/components/ReportsView.tsx">
                  <Eye className="w-5 h-5" data-id="vnazimbpd" data-path="src/components/ReportsView.tsx" />
                  <span data-id="fw392qeqk" data-path="src/components/ReportsView.tsx">Report Preview</span>
                </CardTitle>
              </CardHeader>
              <CardContent data-id="f12wibmf4" data-path="src/components/ReportsView.tsx">
                {!reportData ?
              <div className="text-center py-8" data-id="awn2lo11n" data-path="src/components/ReportsView.tsx">
                    <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" data-id="ze4ge8dly" data-path="src/components/ReportsView.tsx" />
                    <p className="text-muted-foreground" data-id="3mkbdxli3" data-path="src/components/ReportsView.tsx">Select a file to preview the report</p>
                  </div> :

              <div className="space-y-6" data-id="pg89598m6" data-path="src/components/ReportsView.tsx">
                    {/* Data Dictionary */}
                    {reportData.dataDictionary && Object.keys(reportData.dataDictionary).length > 0 &&
                <div data-id="b60wfez49" data-path="src/components/ReportsView.tsx">
                        <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2" data-id="s9zlgnifk" data-path="src/components/ReportsView.tsx">
                          <Database className="w-5 h-5" data-id="nj89n8n5o" data-path="src/components/ReportsView.tsx" />
                          <span data-id="r5o710bfb" data-path="src/components/ReportsView.tsx">Data Dictionary</span>
                        </h3>
                        <div className="space-y-2" data-id="sdd93li13" data-path="src/components/ReportsView.tsx">
                          {Object.entries(reportData.dataDictionary).slice(0, 5).map(([key, value]: [string, any]) =>
                    <div key={key} className="p-3 bg-muted rounded-lg" data-id="6y9n2gxlc" data-path="src/components/ReportsView.tsx">
                              <div className="font-medium" data-id="9u8o5gsbo" data-path="src/components/ReportsView.tsx">{key}</div>
                              <div className="text-sm text-muted-foreground mt-1" data-id="rq15zohzq" data-path="src/components/ReportsView.tsx">
                                {String(value).slice(0, 100)}
                                {String(value).length > 100 ? '...' : ''}
                              </div>
                            </div>
                    )}
                          {Object.keys(reportData.dataDictionary).length > 5 &&
                    <p className="text-sm text-muted-foreground" data-id="1fqzcohj6" data-path="src/components/ReportsView.tsx">
                              +{Object.keys(reportData.dataDictionary).length - 5} more columns in full report
                            </p>
                    }
                        </div>
                      </div>
                }

                    {/* Key Insights */}
                    {reportData.insights &&
                <div data-id="3tb92us1f" data-path="src/components/ReportsView.tsx">
                        <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2" data-id="5zbnzpjlq" data-path="src/components/ReportsView.tsx">
                          <TrendingUp className="w-5 h-5" data-id="qxtvjeccz" data-path="src/components/ReportsView.tsx" />
                          <span data-id="dfps0pmut" data-path="src/components/ReportsView.tsx">Key Insights</span>
                        </h3>
                        <div className="p-4 bg-muted rounded-lg" data-id="od9fs26bs" data-path="src/components/ReportsView.tsx">
                          <p className="text-sm whitespace-pre-wrap" data-id="tn5qx7pb1" data-path="src/components/ReportsView.tsx">
                            {reportData.insights.slice(0, 300)}
                            {reportData.insights.length > 300 ? '...' : ''}
                          </p>
                        </div>
                      </div>
                }

                    {/* Recommendations */}
                    {reportData.recommendations &&
                <div data-id="46t6x63lt" data-path="src/components/ReportsView.tsx">
                        <h3 className="text-lg font-semibold mb-3 flex items-center space-x-2" data-id="okp62dtmo" data-path="src/components/ReportsView.tsx">
                          <CheckCircle className="w-5 h-5" data-id="cqk79vmcg" data-path="src/components/ReportsView.tsx" />
                          <span data-id="pqu9ubjq8" data-path="src/components/ReportsView.tsx">Recommendations</span>
                        </h3>
                        <div className="p-4 bg-muted rounded-lg" data-id="pxtn9hhbm" data-path="src/components/ReportsView.tsx">
                          <p className="text-sm whitespace-pre-wrap" data-id="4gjcviw63" data-path="src/components/ReportsView.tsx">
                            {reportData.recommendations.slice(0, 300)}
                            {reportData.recommendations.length > 300 ? '...' : ''}
                          </p>
                        </div>
                      </div>
                }

                    <div className="text-sm text-muted-foreground" data-id="7cf6fey55" data-path="src/components/ReportsView.tsx">
                      This is a preview. Download the full PDF report for complete analysis.
                    </div>
                  </div>
              }
              </CardContent>
            </Card>
          </div>
        </div>
      }
    </div>);

};

export default ReportsView;