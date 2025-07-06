import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://smzezqtlqndrbesykjoo.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNtemV6cXRscW5kcmJlc3lram9vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIxNDE0MDAsImV4cCI6MjA1NzcxNzQwMH0.RCzrsJ9dnvPaDiOa1g8zDqBo9WaiqZLdDtabm9fMBtw';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export type Database = {
  public: {
    Tables: {
      app_users: {
        Row: {
          id: string;
          user_id: string;
          name: string;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          name: string;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          name?: string;
          created_at?: string;
        };
      };
      file_uploads: {
        Row: {
          id: string;
          user_id: string;
          file_name: string;
          file_path: string;
          file_type: string;
          file_size: number;
          upload_timestamp: string;
          analysis_results?: any;
        };
        Insert: {
          id?: string;
          user_id: string;
          file_name: string;
          file_path: string;
          file_type: string;
          file_size: number;
          upload_timestamp?: string;
          analysis_results?: any;
        };
        Update: {
          id?: string;
          user_id?: string;
          file_name?: string;
          file_path?: string;
          file_type?: string;
          file_size?: number;
          upload_timestamp?: string;
          analysis_results?: any;
        };
      };
    };
  };
};