import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { supabase } from '@/lib/supabase';
import { analyzeDataWithAI } from '@/lib/openrouter';
import { toast } from 'sonner';
import {
  Upload,
  File,
  Database,
  CheckCircle,
  Loader2,
  AlertTriangle } from
'lucide-react';
import Papa from 'papaparse';
import * as XLSX from 'xlsx';

interface FileUploadProps {
  onUploadComplete?: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
  const { user } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [preview, setPreview] = useState<any[]>([]);
  const [dbConnection, setDbConnection] = useState({
    host: '',
    port: '5432',
    database: '',
    username: '',
    password: '',
    table: ''
  });

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    if (!validTypes.includes(file.type) && !file.name.toLowerCase().match(/\.(csv|xlsx|xls)$/)) {
      toast.error('Please upload CSV or Excel files only');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      // Read and parse file for preview
      const fileText = await readFileAsText(file);
      let parsedData: any[] = [];

      if (file.name.toLowerCase().endsWith('.csv')) {
        parsedData = Papa.parse(fileText, { header: true, skipEmptyLines: true }).data;
      } else {
        // Handle Excel files
        const workbook = XLSX.read(fileText, { type: 'binary' });
        const sheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[sheetName];
        parsedData = XLSX.utils.sheet_to_json(sheet);
      }

      setPreview(parsedData.slice(0, 5)); // Show first 5 rows
      setUploadProgress(50);

      // Upload to Supabase Storage
      const fileName = `${user?.user_id}/${Date.now()}_${file.name}`;
      const { data: uploadData, error: uploadError } = await supabase.storage.
      from('data-files').
      upload(fileName, file);

      if (uploadError) {
        throw uploadError;
      }

      setUploadProgress(75);

      // Save file metadata to database
      const { data: fileRecord, error: dbError } = await supabase.
      from('file_uploads').
      insert([
      {
        user_id: user?.user_id,
        file_name: file.name,
        file_path: fileName,
        file_type: file.type,
        file_size: file.size
      }]
      ).
      select().
      single();

      if (dbError) {
        throw dbError;
      }

      setUploadProgress(90);

      // Start AI analysis
      setAnalyzing(true);
      const csvString = Papa.unparse(parsedData.slice(0, 100)); // Send first 100 rows for analysis
      const analysis = await analyzeDataWithAI(csvString, file.name);

      // Update file record with analysis results
      const { error: updateError } = await supabase.
      from('file_uploads').
      update({ analysis_results: analysis }).
      eq('id', fileRecord.id);

      if (updateError) {
        console.error('Error saving analysis:', updateError);
      }

      setUploadProgress(100);
      toast.success('File uploaded and analyzed successfully!');

      if (onUploadComplete) {
        onUploadComplete();
      }

    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
      setAnalyzing(false);
      setUploadProgress(0);
    }
  }, [user, onUploadComplete]);

  const readFileAsText = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = reject;

      if (file.name.toLowerCase().endsWith('.csv')) {
        reader.readAsText(file);
      } else {
        reader.readAsBinaryString(file);
      }
    });
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    multiple: false,
    disabled: uploading
  });

  const connectDatabase = async () => {
    if (!dbConnection.host || !dbConnection.database || !dbConnection.username || !dbConnection.table) {
      toast.error('Please fill in all required database connection fields');
      return;
    }

    setUploading(true);
    try {
      // Note: In a real implementation, you'd handle database connections server-side
      // This is a placeholder for the database connection logic
      toast.info('Database connection feature will be implemented server-side for security');

    } catch (error) {
      console.error('Database connection error:', error);
      toast.error('Failed to connect to database');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-6 space-y-6" data-id="hs2q43nr7" data-path="src/components/FileUpload.tsx">
      <div data-id="ll0y32a3n" data-path="src/components/FileUpload.tsx">
        <h1 className="text-3xl font-bold" data-id="m3gng1jzj" data-path="src/components/FileUpload.tsx">Upload Data</h1>
        <p className="text-muted-foreground mt-1" data-id="qi7z5mz2o" data-path="src/components/FileUpload.tsx">
          Upload CSV/Excel files or connect to databases for analysis
        </p>
      </div>

      <Tabs defaultValue="file" className="space-y-6" data-id="nkf09de1p" data-path="src/components/FileUpload.tsx">
        <TabsList data-id="th2uyuoux" data-path="src/components/FileUpload.tsx">
          <TabsTrigger value="file" data-id="140usjjr1" data-path="src/components/FileUpload.tsx">File Upload</TabsTrigger>
          <TabsTrigger value="database" data-id="socygaz0c" data-path="src/components/FileUpload.tsx">Database Connection</TabsTrigger>
        </TabsList>

        <TabsContent value="file" className="space-y-6" data-id="q0io0z56y" data-path="src/components/FileUpload.tsx">
          <Card data-id="3g66e0em0" data-path="src/components/FileUpload.tsx">
            <CardHeader data-id="acx3otvhx" data-path="src/components/FileUpload.tsx">
              <CardTitle className="flex items-center space-x-2" data-id="irnzlu5wo" data-path="src/components/FileUpload.tsx">
                <Upload className="w-5 h-5" data-id="fjvk83866" data-path="src/components/FileUpload.tsx" />
                <span data-id="qjdynwb8q" data-path="src/components/FileUpload.tsx">File Upload</span>
              </CardTitle>
            </CardHeader>
            <CardContent data-id="5q80u5jlo" data-path="src/components/FileUpload.tsx">
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
                isDragActive ?
                'border-primary bg-primary/5' :
                'border-muted-foreground/25 hover:border-primary/50'} ${
                uploading ? 'opacity-50 cursor-not-allowed' : ''}`} data-id="ca7iqpiiy" data-path="src/components/FileUpload.tsx">

                <input {...getInputProps()} data-id="fgwx9s9wq" data-path="src/components/FileUpload.tsx" />
                <div className="space-y-4" data-id="jdurm0xz9" data-path="src/components/FileUpload.tsx">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto" data-id="c3b8nb2e8" data-path="src/components/FileUpload.tsx">
                    {uploading ?
                    <Loader2 className="w-8 h-8 text-primary animate-spin" data-id="hcqz57cfn" data-path="src/components/FileUpload.tsx" /> :

                    <File className="w-8 h-8 text-primary" data-id="8rv9iz5y9" data-path="src/components/FileUpload.tsx" />
                    }
                  </div>
                  
                  {uploading ?
                  <div className="space-y-2" data-id="jk2liu7fv" data-path="src/components/FileUpload.tsx">
                      <p className="text-lg font-medium" data-id="2fy4a810y" data-path="src/components/FileUpload.tsx">
                        {analyzing ? 'Analyzing with AI...' : 'Uploading...'}
                      </p>
                      <Progress value={uploadProgress} className="w-64 mx-auto" data-id="zwdldtmle" data-path="src/components/FileUpload.tsx" />
                      <p className="text-sm text-muted-foreground" data-id="zy2z7lo1l" data-path="src/components/FileUpload.tsx">
                        {uploadProgress}% complete
                      </p>
                    </div> :
                  isDragActive ?
                  <p className="text-lg font-medium" data-id="x11bfj3ap" data-path="src/components/FileUpload.tsx">Drop your file here...</p> :

                  <div className="space-y-2" data-id="prbiezth3" data-path="src/components/FileUpload.tsx">
                      <p className="text-lg font-medium" data-id="kiwl1d8pa" data-path="src/components/FileUpload.tsx">
                        Drag & drop files here, or click to select
                      </p>
                      <p className="text-muted-foreground" data-id="lzs241l8q" data-path="src/components/FileUpload.tsx">
                        Supports CSV, Excel (.xlsx, .xls) files
                      </p>
                    </div>
                  }
                </div>
              </div>

              {preview.length > 0 &&
              <div className="mt-6" data-id="24qnrxp20" data-path="src/components/FileUpload.tsx">
                  <h3 className="text-lg font-medium mb-3" data-id="u5finqmvz" data-path="src/components/FileUpload.tsx">Data Preview</h3>
                  <div className="border rounded-lg overflow-auto max-h-64" data-id="tuzecdlrn" data-path="src/components/FileUpload.tsx">
                    <table className="w-full text-sm" data-id="8a33rk3m9" data-path="src/components/FileUpload.tsx">
                      <thead className="bg-muted" data-id="tm3weoily" data-path="src/components/FileUpload.tsx">
                        <tr data-id="p1utjewg9" data-path="src/components/FileUpload.tsx">
                          {Object.keys(preview[0] || {}).map((header) =>
                        <th key={header} className="p-2 text-left font-medium" data-id="drp66fjrw" data-path="src/components/FileUpload.tsx">
                              {header}
                            </th>
                        )}
                        </tr>
                      </thead>
                      <tbody data-id="tbvt0mpvi" data-path="src/components/FileUpload.tsx">
                        {preview.map((row, index) =>
                      <tr key={index} className="border-t" data-id="ptcqv9qhw" data-path="src/components/FileUpload.tsx">
                            {Object.values(row).map((value: any, cellIndex) =>
                        <td key={cellIndex} className="p-2" data-id="f3ncockrp" data-path="src/components/FileUpload.tsx">
                                {String(value || '').slice(0, 50)}
                                {String(value || '').length > 50 ? '...' : ''}
                              </td>
                        )}
                          </tr>
                      )}
                      </tbody>
                    </table>
                  </div>
                </div>
              }
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="database" className="space-y-6" data-id="9igjwodog" data-path="src/components/FileUpload.tsx">
          <Card data-id="vbqjmys0g" data-path="src/components/FileUpload.tsx">
            <CardHeader data-id="gi183ir5z" data-path="src/components/FileUpload.tsx">
              <CardTitle className="flex items-center space-x-2" data-id="h6bkky2dw" data-path="src/components/FileUpload.tsx">
                <Database className="w-5 h-5" data-id="jiuav91vp" data-path="src/components/FileUpload.tsx" />
                <span data-id="9y3pzq15e" data-path="src/components/FileUpload.tsx">Database Connection</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4" data-id="jau4be7c3" data-path="src/components/FileUpload.tsx">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-id="sf3rwm83l" data-path="src/components/FileUpload.tsx">
                <div className="space-y-2" data-id="2rknev128" data-path="src/components/FileUpload.tsx">
                  <Label htmlFor="host" data-id="eerd8ic9d" data-path="src/components/FileUpload.tsx">Host *</Label>
                  <Input
                    id="host"
                    placeholder="localhost"
                    value={dbConnection.host}
                    onChange={(e) => setDbConnection((prev) => ({ ...prev, host: e.target.value }))} data-id="nwz4hjoxj" data-path="src/components/FileUpload.tsx" />

                </div>
                <div className="space-y-2" data-id="2njq8m2pl" data-path="src/components/FileUpload.tsx">
                  <Label htmlFor="port" data-id="ru4dbrz3d" data-path="src/components/FileUpload.tsx">Port</Label>
                  <Input
                    id="port"
                    placeholder="5432"
                    value={dbConnection.port}
                    onChange={(e) => setDbConnection((prev) => ({ ...prev, port: e.target.value }))} data-id="l9mme2hg8" data-path="src/components/FileUpload.tsx" />

                </div>
                <div className="space-y-2" data-id="85sdiqh2u" data-path="src/components/FileUpload.tsx">
                  <Label htmlFor="database" data-id="mnw50tx67" data-path="src/components/FileUpload.tsx">Database *</Label>
                  <Input
                    id="database"
                    placeholder="my_database"
                    value={dbConnection.database}
                    onChange={(e) => setDbConnection((prev) => ({ ...prev, database: e.target.value }))} data-id="cgcv4nwqi" data-path="src/components/FileUpload.tsx" />

                </div>
                <div className="space-y-2" data-id="6lvyamksn" data-path="src/components/FileUpload.tsx">
                  <Label htmlFor="username" data-id="z0vd5vph8" data-path="src/components/FileUpload.tsx">Username *</Label>
                  <Input
                    id="username"
                    placeholder="postgres"
                    value={dbConnection.username}
                    onChange={(e) => setDbConnection((prev) => ({ ...prev, username: e.target.value }))} data-id="67wo36uml" data-path="src/components/FileUpload.tsx" />

                </div>
                <div className="space-y-2" data-id="t4vfzl367" data-path="src/components/FileUpload.tsx">
                  <Label htmlFor="password" data-id="ob144bg25" data-path="src/components/FileUpload.tsx">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter password"
                    value={dbConnection.password}
                    onChange={(e) => setDbConnection((prev) => ({ ...prev, password: e.target.value }))} data-id="98p0xq079" data-path="src/components/FileUpload.tsx" />

                </div>
                <div className="space-y-2" data-id="k4u8lgbg7" data-path="src/components/FileUpload.tsx">
                  <Label htmlFor="table" data-id="18id7sww3" data-path="src/components/FileUpload.tsx">Table Name *</Label>
                  <Input
                    id="table"
                    placeholder="my_table"
                    value={dbConnection.table}
                    onChange={(e) => setDbConnection((prev) => ({ ...prev, table: e.target.value }))} data-id="4b5o48qp8" data-path="src/components/FileUpload.tsx" />

                </div>
              </div>

              <div className="flex items-start space-x-2 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg" data-id="7emkyp51u" data-path="src/components/FileUpload.tsx">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" data-id="0w6anylts" data-path="src/components/FileUpload.tsx" />
                <div className="text-sm" data-id="q58sjvkex" data-path="src/components/FileUpload.tsx">
                  <p className="font-medium text-yellow-800 dark:text-yellow-200" data-id="cvpddzri2" data-path="src/components/FileUpload.tsx">
                    Database Connection Notice
                  </p>
                  <p className="text-yellow-700 dark:text-yellow-300" data-id="y4id5t4e8" data-path="src/components/FileUpload.tsx">
                    Database connections will be processed securely on our servers to protect your credentials.
                  </p>
                </div>
              </div>

              <Button onClick={connectDatabase} disabled={uploading} className="w-full" data-id="5zh39nua7" data-path="src/components/FileUpload.tsx">
                {uploading ?
                <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" data-id="0ewhr5sge" data-path="src/components/FileUpload.tsx" />
                    Connecting...
                  </> :

                <>
                    <Database className="w-4 h-4 mr-2" data-id="4rqrne9jt" data-path="src/components/FileUpload.tsx" />
                    Test Connection & Import Data
                  </>
                }
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>);

};

export default FileUpload;