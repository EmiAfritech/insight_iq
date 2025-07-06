// src/api/connect-database.ts
import { Client } from 'pg';
import { createClient } from '@supabase/supabase-js';
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { host, port, database, username, password, table, user_id } = req.body;

  try {
    // Test connection
    const client = new Client({
      host,
      port: parseInt(port),
      database,
      user: username,
      password,
      ssl: { rejectUnauthorized: false },
    });

    await client.connect();
    const { rows } = await client.query(`SELECT * FROM ${table} LIMIT 5`);
    await client.end();

    // Save connection via Supabase Admin (bypass RLS)
    const supabaseAdmin = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY! // Critical for RLS bypass
    );

    const { data, error } = await supabaseAdmin
      .from('database_connections')
      .insert([{
        user_id,
        host,
        port: parseInt(port),
        database,
        username,
        table_name: table,
        status: 'connected',
        sample_data: rows,
      }])
      .select()
      .single();

    if (error) throw error;
    res.status(200).json({ sampleData: rows });
  } catch (error: any) {
    console.error('Database error:', error.message);
    res.status(500).json({ error: error.message || 'Connection failed' });
  }
}

