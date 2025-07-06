// import React, { useState, useCallback } from 'react';
// import { useDropzone } from 'react-dropzone';
// import { useAuth } from '@/contexts/AuthContext';
// import { Button } from '@/components/ui/button';
// import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
// import { Input } from '@/components/ui/input';
// import { Label } from '@/components/ui/label';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import { Progress } from '@/components/ui/progress';
// import { supabase } from '@/lib/supabase';
// import { analyzeDataWithAI } from '@/lib/openrouter';
// import { toast } from 'sonner';
// import { Upload, File, Database, Loader2, AlertTriangle } from 'lucide-react';
// import Papa from 'papaparse';
// import * as XLSX from 'xlsx';

// interface FileUploadProps {
//   onUploadComplete?: () => void;
// }

// const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
//   const { user } = useAuth();
//   const [uploading, setUploading] = useState(false);
//   const [analyzing, setAnalyzing] = useState(false);
//   const [uploadProgress, setUploadProgress] = useState(0);
//   const [preview, setPreview] = useState<any[]>([]);
//   const [dbConnection, setDbConnection] = useState({
//     host: process.env.POSTGRES_HOST || '',
//     port: process.env.POSTGRES_PORT || '5432',
//     database: process.env.POSTGRES_DB || '',
//     username: process.env.POSTGRES_USER || '',
//     password: '',
//     table: ''
//   });

//   const onDrop = useCallback(async (acceptedFiles: File[]) => {
//     const file = acceptedFiles[0];
//     if (!file || !user?.user_id) {
//       toast.error('No file selected or user not authenticated');
//       return;
//     }

//     // Validate file
//     const validTypes = [
//       'text/csv',
//       'application/vnd.ms-excel',
//       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
//     ];
//     const maxSize = 10 * 1024 * 1024; // 10MB

//     if (!validTypes.includes(file.type) && !/\.(csv|xlsx|xls)$/i.test(file.name)) {
//       toast.error('Only CSV and Excel files are allowed');
//       return;
//     }

//     if (file.size > maxSize) {
//       toast.error('File size exceeds 10MB limit');
//       return;
//     }

//     setUploading(true);
//     setUploadProgress(0);

//     try {
//       // Parse file
//       const fileText = await new Promise<string>((resolve, reject) => {
//         const reader = new FileReader();
//         reader.onload = (e) => resolve(e.target?.result as string);
//         reader.onerror = reject;
//         file.name.toLowerCase().endsWith('.csv') ? reader.readAsText(file) : reader.readAsBinaryString(file);
//       });

//       let parsedData: any[] = [];
//       if (file.name.toLowerCase().endsWith('.csv')) {
//         parsedData = Papa.parse(fileText, { header: true, skipEmptyLines: true }).data;
//       } else {
//         const workbook = XLSX.read(fileText, { type: 'binary' });
//         parsedData = XLSX.utils.sheet_to_json(workbook.Sheets[workbook.SheetNames[0]]);
//       }

//       setPreview(parsedData.slice(0, 5));
//       setUploadProgress(30);

//       // Upload to storage
//       const fileName = `${user.user_id}/${Date.now()}_${file.name}`;
//       const { error: uploadError } = await supabase.storage
//         .from('uploads')
//         .upload(fileName, file, {
//           cacheControl: '3600',
//           upsert: false,
//         });

//       if (uploadError) throw uploadError;
//       setUploadProgress(70);

//       // Save to database via API (bypasses RLS)
//       const response = await fetch('/src/api/save-file-metadata.ts', {
//         method: 'POST',
//         headers: { 
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`
//         },
//         body: JSON.stringify({
//           user_id: user.user_id,
//           file_name: file.name,
//           file_path: fileName,
//           file_type: file.type,
//           file_size: file.size,
//         }),
//       });

//       if (!response.ok) throw new Error(await response.text());
//       const fileRecord = await response.json();
//       setUploadProgress(90);

//       // AI analysis using your openrouter.ts
//       setAnalyzing(true);
//       const analysis = await analyzeDataWithAI(
//         Papa.unparse(parsedData.slice(0, 100)), 
//         file.name
//       );

//       // Update with analysis
//       const updateResponse = await fetch('src/api/update-file-analysis', {
//         method: 'POST',
//         headers: { 
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`
//         },
//         body: JSON.stringify({
//           file_id: fileRecord.id,
//           analysis_results: analysis,
//         }),
//       });

//       if (!updateResponse.ok) throw new Error(await updateResponse.text());

//       setUploadProgress(100);
//       toast.success('File processed successfully!');
//       onUploadComplete?.();
//     } catch (error: any) {
//       console.error('Upload error:', error);
//       toast.error(error.message || 'File processing failed');
//     } finally {
//       setUploading(false);
//       setAnalyzing(false);
//     }
//   }, [user, onUploadComplete]);

//   const connectDatabase = async () => {
//     const requiredFields = ['host', 'database', 'username', 'table'];
//     const missingFields = requiredFields.filter(field => !dbConnection[field as keyof typeof dbConnection]);

//     if (missingFields.length > 0 || !user?.user_id) {
//       toast.error(`Missing required fields: ${missingFields.join(', ')}`);
//       return;
//     }

//     setUploading(true);

//     try {
//       const response = await fetch('src/api/connect-database', {
//         method: 'POST',
//         headers: { 
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`
//         },
//         body: JSON.stringify({
//           ...dbConnection,
//           user_id: user.user_id,
//         }),
//       });

//       if (!response.ok) throw new Error(await response.text());
//       const result = await response.json();

//       toast.success('Database connected successfully!');
//       setPreview(result.sampleData || []);
//       onUploadComplete?.();
//     } catch (error: any) {
//       console.error('Database error:', error);
//       toast.error(error.message || 'Database connection failed');
//     } finally {
//       setUploading(false);
//     }
//   };

//   const { getRootProps, getInputProps, isDragActive } = useDropzone({
//     onDrop,
//     accept: {
//       'text/csv': ['.csv'],
//       'application/vnd.ms-excel': ['.xls'],
//       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
//     },
//     multiple: false,
//     disabled: uploading,
//     maxSize: 10 * 1024 * 1024,
//   });

//   return (
//     <div className="p-6 space-y-6">
//       <div>
//         <h1 className="text-3xl font-bold">Upload Data</h1>
//         <p className="text-muted-foreground mt-1">
//           Upload CSV/Excel files or connect to databases for analysis
//         </p>
//       </div>

//       <Tabs defaultValue="file" className="space-y-6">
//         <TabsList>
//           <TabsTrigger value="file">File Upload</TabsTrigger>
//           <TabsTrigger value="database">Database Connection</TabsTrigger>
//         </TabsList>

//         <TabsContent value="file" className="space-y-6">
//           <Card>
//             <CardHeader>
//               <CardTitle className="flex items-center space-x-2">
//                 <Upload className="w-5 h-5" />
//                 <span>File Upload</span>
//               </CardTitle>
//             </CardHeader>
//             <CardContent>
//               <div
//                 {...getRootProps()}
//                 className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
//                   isDragActive
//                     ? 'border-primary bg-primary/5'
//                     : 'border-muted-foreground/25 hover:border-primary/50'
//                 } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
//               >
//                 <input {...getInputProps()} />
//                 <div className="space-y-4">
//                   <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
//                     {uploading ? (
//                       <Loader2 className="w-8 h-8 text-primary animate-spin" />
//                     ) : (
//                       <File className="w-8 h-8 text-primary" />
//                     )}
//                   </div>

//                   {uploading ? (
//                     <div className="space-y-2">
//                       <p className="text-lg font-medium">
//                         {analyzing ? 'Analyzing with AI...' : 'Uploading...'}
//                       </p>
//                       <Progress
//                         value={uploadProgress}
//                         className="w-64 mx-auto"
//                       />
//                       <p className="text-sm text-muted-foreground">
//                         {uploadProgress}% complete
//                       </p>
//                     </div>
//                   ) : isDragActive ? (
//                     <p className="text-lg font-medium">Drop your file here...</p>
//                   ) : (
//                     <div className="space-y-2">
//                       <p className="text-lg font-medium">
//                         Drag & drop files here, or click to select
//                       </p>
//                       <p className="text-muted-foreground">
//                         Supports CSV, Excel (.xlsx, .xls) files (Max 10MB)
//                       </p>
//                     </div>
//                   )}
//                 </div>
//               </div>

//               {preview.length > 0 && (
//                 <div className="mt-6">
//                   <h3 className="text-lg font-medium mb-3">Data Preview</h3>
//                   <div className="border rounded-lg overflow-auto max-h-64">
//                     <table className="w-full text-sm">
//                       <thead className="bg-muted">
//                         <tr>
//                           {Object.keys(preview[0]).map((header) => (
//                             <th key={header} className="p-2 text-left font-medium">
//                               {header}
//                             </th>
//                           ))}
//                         </tr>
//                       </thead>
//                       <tbody>
//                         {preview.map((row, index) => (
//                           <tr key={index} className="border-t">
//                             {Object.values(row).map((value: any, cellIndex) => (
//                               <td key={cellIndex} className="p-2">
//                                 {String(value || '').slice(0, 50)}
//                                 {String(value || '').length > 50 ? '...' : ''}
//                               </td>
//                             ))}
//                           </tr>
//                         ))}
//                       </tbody>
//                     </table>
//                   </div>
//                 </div>
//               )}
//             </CardContent>
//           </Card>
//         </TabsContent>

//         <TabsContent value="database" className="space-y-6">
//           <Card>
//             <CardHeader>
//               <CardTitle className="flex items-center space-x-2">
//                 <Database className="w-5 h-5" />
//                 <span>Database Connection</span>
//               </CardTitle>
//             </CardHeader>
//             <CardContent className="space-y-4">
//               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//                 <div className="space-y-2">
//                   <Label htmlFor="host">Host *</Label>
//                   <Input
//                     id="host"
//                     value={dbConnection.host}
//                     onChange={(e) => setDbConnection(p => ({ ...p, host: e.target.value }))}
//                   />
//                 </div>
//                 <div className="space-y-2">
//                   <Label htmlFor="port">Port *</Label>
//                   <Input
//                     id="port"
//                     value={dbConnection.port}
//                     onChange={(e) => setDbConnection(p => ({ ...p, port: e.target.value }))}
//                   />
//                 </div>
//                 <div className="space-y-2">
//                   <Label htmlFor="database">Database *</Label>
//                   <Input
//                     id="database"
//                     value={dbConnection.database}
//                     onChange={(e) => setDbConnection(p => ({ ...p, database: e.target.value }))}
//                   />
//                 </div>
//                 <div className="space-y-2">
//                   <Label htmlFor="username">Username *</Label>
//                   <Input
//                     id="username"
//                     value={dbConnection.username}
//                     onChange={(e) => setDbConnection(p => ({ ...p, username: e.target.value }))}
//                   />
//                 </div>
//                 <div className="space-y-2">
//                   <Label htmlFor="password">Password *</Label>
//                   <Input
//                     id="password"
//                     type="password"
//                     value={dbConnection.password}
//                     onChange={(e) => setDbConnection(p => ({ ...p, password: e.target.value }))}
//                   />
//                 </div>
//                 <div className="space-y-2">
//                   <Label htmlFor="table">Table Name *</Label>
//                   <Input
//                     id="table"
//                     value={dbConnection.table}
//                     onChange={(e) => setDbConnection(p => ({ ...p, table: e.target.value }))}
//                   />
//                 </div>
//               </div>

//               <div className="flex items-start space-x-2 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
//                 <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
//                 <div className="text-sm">
//                   <p className="font-medium text-yellow-800 dark:text-yellow-200">
//                     Database Connection Notice
//                   </p>
//                   <p className="text-yellow-700 dark:text-yellow-300">
//                     Credentials are encrypted and only used for this session.
//                   </p>
//                 </div>
//               </div>

//               <Button
//                 onClick={connectDatabase}
//                 disabled={uploading}
//                 className="w-full"
//               >
//                 {uploading ? (
//                   <>
//                     <Loader2 className="w-4 h-4 mr-2 animate-spin" />
//                     Connecting...
//                   </>
//                 ) : (
//                   <>
//                     <Database className="w-4 h-4 mr-2" />
//                     Connect & Import Data
//                   </>
//                 )}
//               </Button>
//             </CardContent>
//           </Card>
//         </TabsContent>
//       </Tabs>
//     </div>
//   );
// };

// export default FileUpload;


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
import { toast } from 'sonner';
import { Upload, File, Database, Loader2, AlertTriangle } from 'lucide-react';
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
    host: process.env.POSTGRES_HOST || '',
    port: process.env.POSTGRES_PORT || '5432',
    database: process.env.POSTGRES_DB || '',
    username: process.env.POSTGRES_USER || '',
    password: '',
    table: ''
  });

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file || !user?.user_id) {
      toast.error('No file selected or user not authenticated');
      return;
    }

    // Validate file
    const validTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!validTypes.includes(file.type) && !/\.(csv|xlsx|xls)$/i.test(file.name)) {
      toast.error('Only CSV and Excel files are allowed');
      return;
    }

    if (file.size > maxSize) {
      toast.error('File size exceeds 10MB limit');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      // Parse file
      const fileText = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target?.result as string);
        reader.onerror = reject;
        file.name.toLowerCase().endsWith('.csv') ? reader.readAsText(file) : reader.readAsBinaryString(file);
      });

      let parsedData: any[] = [];
      if (file.name.toLowerCase().endsWith('.csv')) {
        parsedData = Papa.parse(fileText, { header: true, skipEmptyLines: true }).data;
      } else {
        const workbook = XLSX.read(fileText, { type: 'binary' });
        parsedData = XLSX.utils.sheet_to_json(workbook.Sheets[workbook.SheetNames[0]]);
      }

      setPreview(parsedData.slice(0, 5));
      setUploadProgress(30);

      // Upload to storage only - no database operations
      const fileName = `${user.user_id}/${Date.now()}_${file.name}`;
      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('uploads')
        .upload(fileName, file, {
          cacheControl: '3600',
          upsert: false,
        });

      if (uploadError) {
        console.error('Storage Upload Error:', {
          message: uploadError.message,
          stack: uploadError.stack,
          details: uploadError
        });
        throw new Error(`Storage upload failed: ${uploadError.message}`);
      }

      setUploadProgress(100);
      toast.success('File uploaded successfully!');
      onUploadComplete?.();
    } catch (error: any) {
      console.error('Upload Process Error:', {
        error: error,
        message: error.message,
        stack: error.stack
      });
      toast.error(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
      setAnalyzing(false);
    }
  }, [user, onUploadComplete]);

  const connectDatabase = async () => {
    const requiredFields = ['host', 'database', 'username', 'table'];
    const missingFields = requiredFields.filter(field => !dbConnection[field as keyof typeof dbConnection]);

    if (missingFields.length > 0 || !user?.user_id) {
      toast.error(`Missing required fields: ${missingFields.join(', ')}`);
      return;
    }

    setUploading(true);

    try {
      const response = await fetch('/api/connect-database', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`
        },
        body: JSON.stringify({
          ...dbConnection,
          user_id: user.user_id,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Database connection failed');
      }

      const result = await response.json();
      toast.success('Database connected successfully!');
      setPreview(result.sampleData || []);
      onUploadComplete?.();
    } catch (error: any) {
      console.error('Database Connection Error:', {
        error: error,
        message: error.message,
        stack: error.stack
      });
      toast.error(error.message || 'Database connection failed');
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    multiple: false,
    disabled: uploading,
    maxSize: 10 * 1024 * 1024,
    onDragEnter: undefined,
    onDragOver: undefined,
    onDragLeave: undefined
  });

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Upload Data</h1>
        <p className="text-muted-foreground mt-1">
          Upload CSV/Excel files or connect to databases for analysis
        </p>
      </div>

      <Tabs defaultValue="file" className="space-y-6">
        <TabsList>
          <TabsTrigger value="file">File Upload</TabsTrigger>
          <TabsTrigger value="database">Database Connection</TabsTrigger>
        </TabsList>

        <TabsContent value="file" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="w-5 h-5" />
                <span>File Upload</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary bg-primary/5'
                    : 'border-muted-foreground/25 hover:border-primary/50'
                } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <input {...getInputProps()} />
                <div className="space-y-4">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                    {uploading ? (
                      <Loader2 className="w-8 h-8 text-primary animate-spin" />
                    ) : (
                      <File className="w-8 h-8 text-primary" />
                    )}
                  </div>

                  {uploading ? (
                    <div className="space-y-2">
                      <p className="text-lg font-medium">
                        {analyzing ? 'Analyzing...' : 'Uploading...'}
                      </p>
                      <Progress
                        value={uploadProgress}
                        className="w-64 mx-auto"
                      />
                      <p className="text-sm text-muted-foreground">
                        {uploadProgress}% complete
                      </p>
                    </div>
                  ) : isDragActive ? (
                    <p className="text-lg font-medium">Drop your file here...</p>
                  ) : (
                    <div className="space-y-2">
                      <p className="text-lg font-medium">
                        Drag & drop files here, or click to select
                      </p>
                      <p className="text-muted-foreground">
                        Supports CSV, Excel (.xlsx, .xls) files (Max 10MB)
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {preview.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-medium mb-3">Data Preview</h3>
                  <div className="border rounded-lg overflow-auto max-h-64">
                    <table className="w-full text-sm">
                      <thead className="bg-muted">
                        <tr>
                          {Object.keys(preview[0]).map((header) => (
                            <th key={header} className="p-2 text-left font-medium">
                              {header}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {preview.map((row, index) => (
                          <tr key={index} className="border-t">
                            {Object.values(row).map((value: any, cellIndex) => (
                              <td key={cellIndex} className="p-2">
                                {String(value || '').slice(0, 50)}
                                {String(value || '').length > 50 ? '...' : ''}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="database" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="w-5 h-5" />
                <span>Database Connection</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="host">Host *</Label>
                  <Input
                    id="host"
                    value={dbConnection.host}
                    onChange={(e) => setDbConnection(p => ({ ...p, host: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="port">Port *</Label>
                  <Input
                    id="port"
                    value={dbConnection.port}
                    onChange={(e) => setDbConnection(p => ({ ...p, port: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="database">Database *</Label>
                  <Input
                    id="database"
                    value={dbConnection.database}
                    onChange={(e) => setDbConnection(p => ({ ...p, database: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="username">Username *</Label>
                  <Input
                    id="username"
                    value={dbConnection.username}
                    onChange={(e) => setDbConnection(p => ({ ...p, username: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password *</Label>
                  <Input
                    id="password"
                    type="password"
                    value={dbConnection.password}
                    onChange={(e) => setDbConnection(p => ({ ...p, password: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="table">Table Name *</Label>
                  <Input
                    id="table"
                    value={dbConnection.table}
                    onChange={(e) => setDbConnection(p => ({ ...p, table: e.target.value }))}
                  />
                </div>
              </div>

              <div className="flex items-start space-x-2 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-yellow-800 dark:text-yellow-200">
                    Database Connection Notice
                  </p>
                  <p className="text-yellow-700 dark:text-yellow-300">
                    Credentials are encrypted and only used for this session.
                  </p>
                </div>
              </div>

              <Button
                onClick={connectDatabase}
                disabled={uploading}
                className="w-full"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Database className="w-4 h-4 mr-2" />
                    Connect & Import Data Live
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FileUpload;