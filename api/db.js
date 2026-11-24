import { Pool } from '@neondatabase/serverless';

const connectionString = process.env.DATABASE_URL || 'postgresql://neondb_owner:npg_kSJ9La4cECpq@ep-little-hat-bkmnlplt-pooler.c-2.ap-southeast-2.aws.neon.tech/neondb?sslmode=require';

const pool = new Pool({ connectionString });

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const client = await pool.connect();
  try {
    if (req.method === 'GET') {
      const { type } = req.query;

      if (type === 'all') {
        const users = await client.query('SELECT id, username, password_hash, name, role, email, client_id FROM users');
        const clients = await client.query('SELECT id, name, pan, gstin, type, phone, email, billing_rate FROM clients');
        const tasks = await client.query('SELECT id, client_id AS client, title, type, emp_id AS emp, TO_CHAR(due_date, \'YYYY-MM-DD\') AS due, priority, status, est_hours AS "estHours", billable, TO_CHAR(completed_on, \'YYYY-MM-DD\') AS "completedOn", completed_by AS "completedBy" FROM tasks');
        const logs = await client.query('SELECT id, TO_CHAR(date, \'YYYY-MM-DD\') AS date, client_id AS client, emp_id AS emp, work, hours, billable FROM logs');
        const compliances = await client.query('SELECT id, title, category AS cat, period, TO_CHAR(due_date, \'YYYY-MM-DD\') AS due, penalty FROM compliances');

        return res.status(200).json({
          users: users.rows,
          clients: clients.rows,
          tasks: tasks.rows,
          logs: logs.rows,
          compliances: compliances.rows
        });
      }

      return res.status(200).json({ status: 'Neon PostgreSQL Connected' });
    }

    if (req.method === 'POST') {
      const { action, table, data, id } = req.body;

      if (action === 'insert') {
        if (table === 'tasks') {
          await client.query(
            `INSERT INTO tasks (id, client_id, title, type, emp_id, due_date, priority, status, est_hours, billable)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
             ON CONFLICT (id) DO UPDATE SET
             client_id = EXCLUDED.client_id,
             title = EXCLUDED.title,
             type = EXCLUDED.type,
             emp_id = EXCLUDED.emp_id,
             due_date = EXCLUDED.due_date,
             priority = EXCLUDED.priority,
             status = EXCLUDED.status,
             est_hours = EXCLUDED.est_hours,
             billable = EXCLUDED.billable`,
            [data.id, data.client, data.title, data.type, data.emp, data.due || null, data.priority, data.status, data.estHours || 0, data.billable !== false]
          );
        } else if (table === 'logs') {
          await client.query(
            `INSERT INTO logs (id, date, client_id, emp_id, work, hours, billable)
             VALUES ($1, $2, $3, $4, $5, $6, $7)
             ON CONFLICT (id) DO UPDATE SET
             date = EXCLUDED.date,
             client_id = EXCLUDED.client_id,
             emp_id = EXCLUDED.emp_id,
             work = EXCLUDED.work,
             hours = EXCLUDED.hours,
             billable = EXCLUDED.billable`,
            [data.id, data.date, data.client, data.emp, data.work, data.hours || 1, data.billable !== false]
          );
        } else if (table === 'clients') {
          await client.query(
            `INSERT INTO clients (id, name, pan, gstin, type, phone, email, billing_rate)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
             ON CONFLICT (id) DO UPDATE SET
             name = EXCLUDED.name,
             pan = EXCLUDED.pan,
             gstin = EXCLUDED.gstin,
             type = EXCLUDED.type,
             phone = EXCLUDED.phone,
             email = EXCLUDED.email,
             billing_rate = EXCLUDED.billing_rate`,
            [data.id, data.name, data.pan, data.gstin, data.type, data.phone, data.email, data.billingRate || 1500]
          );
        } else if (table === 'users') {
          await client.query(
            `INSERT INTO users (id, username, password_hash, name, role, email, client_id)
             VALUES ($1, $2, $3, $4, $5, $6, $7)
             ON CONFLICT (id) DO UPDATE SET
             password_hash = EXCLUDED.password_hash,
             name = EXCLUDED.name,
             role = EXCLUDED.role,
             email = EXCLUDED.email,
             client_id = EXCLUDED.client_id`,
            [data.id, data.username, data.password_hash, data.name, data.role, data.email, data.client_id]
          );
        }
        return res.status(200).json({ success: true });
      }

      if (action === 'delete') {
        const allowedTables = ['tasks', 'logs', 'clients', 'users', 'compliances'];
        if (allowedTables.includes(table)) {
          await client.query(`DELETE FROM ${table} WHERE id = $1`, [id]);
          return res.status(200).json({ success: true });
        }
      }

      if (action === 'update_task_done') {
        await client.query(
          `UPDATE tasks SET status = 'Completed', completed_on = $1, completed_by = $2 WHERE id = $3`,
          [data.completedOn, data.completedBy, id]
        );
        return res.status(200).json({ success: true });
      }

      return res.status(400).json({ error: 'Unsupported action' });
    }

    res.status(405).json({ error: 'Method Not Allowed' });
  } catch (error) {
    console.error('Database Error:', error);
    res.status(500).json({ error: error.message });
  } finally {
    client.release();
  }
}
