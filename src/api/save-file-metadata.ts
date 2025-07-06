
// // src/api/save-file-metadata.ts
// import type { NextApiRequest, NextApiResponse } from 'next';
// import { createClient } from '@supabase/supabase-js';

// // Debug: Log environment check at the top (only logs on server)
// console.log('[ENV CHECK] Supabase URL:', process.env.SUPABASE_URL?.slice(0, 20));
// console.log('[ENV CHECK] Service Role Key Prefix:', process.env.SUPABASE_SERVICE_ROLE_KEY?.slice(0, 5));

// const supabaseAdmin = createClient(
//   process.env.SUPABASE_URL || '',
//   process.env.SUPABASE_SERVICE_ROLE_KEY || ''
// );

// export default async function handler(req: NextApiRequest, res: NextApiResponse) {
//   if (req.method !== 'POST') {
//     return res.status(405).json({ error: 'Method not allowed' });
//   }

//   const {
//     user_id,
//     file_name,
//     file_path,
//     file_type,
//     file_size
//   } = req.body;

//   // Validate input
//   if (!user_id || !file_name || !file_path || !file_type || !file_size) {
//     return res.status(400).json({ error: 'Missing required fields' });
//   }

//   try {
//     const { data, error } = await supabaseAdmin
//       .from('file_uploads')
//       .insert([{
//         user_id,
//         file_name,
//         file_path,
//         file_type,
//         file_size
//       }])
//       .select()
//       .single();

//     if (error) {
//       console.error('Supabase insert error:', error);
//       return res.status(500).json({ error: 'Failed to save metadata', details: error.message });
//     }

//     return res.status(200).json(data);
//   } catch (err: any) {
//     console.error('Unhandled error:', err);
//     return res.status(500).json({ error: 'Internal server error', details: err.message });
//   }
// }

// src/api/save-file-metadata.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

// 🔐 Directly injected keys for testing
const supabaseUrl = 'https://smzezqtlqndrbesykjoo.supabase.co';
const supabaseServiceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNtemV6cXRscW5kcmJlc3lram9vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MjE0MTQwMCwiZXhwIjoyMDU3NzE3NDAwfQ.yAWyguNceBryhhEbKLY51ati7VLZufTmG-_UfayqJ2w';

const supabaseAdmin = createClient(supabaseUrl, supabaseServiceRoleKey);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const {
    user_id,
    file_name,
    file_path,
    file_type,
    file_size
  } = req.body;

  if (!user_id || !file_name || !file_path || !file_type || !file_size) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  try {
    const { data, error } = await supabaseAdmin
      .from('file_uploads')
      .insert([{
        user_id,
        file_name,
        file_path,
        file_type,
        file_size
      }])
      .select()
      .single();

    if (error) {
      console.error('Supabase insert error:', error);
      return res.status(500).json({ error: 'Failed to save metadata', details: error.message });
    }

    return res.status(200).json(data);
  } catch (err: any) {
    console.error('Unhandled error:', err);
    return res.status(500).json({ error: 'Internal server error', details: err.message });
  }
}
