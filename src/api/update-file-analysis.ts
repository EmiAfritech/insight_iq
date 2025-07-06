// import { createClient } from '@supabase/supabase-js';
// import type { NextApiRequest, NextApiResponse } from 'next';

// export default async function handler(
//   req: NextApiRequest,
//   res: NextApiResponse
// ) {
//   if (req.method !== 'POST') {
//     return res.status(405).json({ error: 'Method not allowed' });
//   }

//   const { file_id, analysis_results } = req.body;

//   try {
//     const supabaseAdmin = createClient(
//       process.env.SUPABASE_URL!,
//       process.env.SUPABASE_SERVICE_ROLE_KEY!
//     );

//     const { error } = await supabaseAdmin
//       .from('file_uploads')
//       .update({ analysis_results })
//       .eq('id', file_id);

//     if (error) throw error;
//     res.status(200).json({ success: true });
//   } catch (error) {
//     console.error('Error updating analysis:', error);
//     res.status(500).json({ error: 'Failed to update analysis' });
//   }
// }

// pages/api/update-file-analysis.ts
import { createClient } from '@supabase/supabase-js';
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { file_id, analysis_results } = req.body;

  // Validate required fields
  if (!file_id || !analysis_results) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  try {
    // Use service role key server-side to bypass RLS
    const supabaseAdmin = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );

    const { data, error } = await supabaseAdmin
      .from('file_uploads')
      .update({ 
        analysis_results,
        status: 'analyzed',
        updated_at: new Date().toISOString()
      })
      .eq('id', file_id)
      .select()
      .single();

    if (error) {
      console.error('Supabase error:', error);
      throw new Error(`Database error: ${error.message}`);
    }

    res.status(200).json({ success: true, data });
  } catch (error: any) {
    console.error('Update analysis error:', error);
    res.status(500).json({ 
      error: error.message || 'Failed to update analysis' 
    });
  }
}