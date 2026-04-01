from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
import mysql.connector
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Static application info metric
metrics.info('jobpulse_app_info', 'JobPulse API information', version='1.0.0')


def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        user=os.getenv('DB_USER', 'jpuser'),
        password=os.getenv('DB_PASS', 'JobPulse2024!'),
        database='jobpulse'
    )


@app.route('/health')
def health():
    try:
        db = get_db()
        db.close()
        logger.info('Health check passed')
        return jsonify({'status': 'ok', 'service': 'jobpulse-api', 'database': 'connected'}), 200
    except Exception as e:
        logger.error(f'Health check failed: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/jobs', methods=['GET'])
def list_jobs():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM jobs ORDER BY created_at DESC LIMIT 100')
        jobs = cursor.fetchall()
        cursor.close()
        db.close()
        logger.info(f'Listed {len(jobs)} jobs')
        return jsonify(jobs), 200
    except Exception as e:
        logger.error(f'Failed to list jobs: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/jobs', methods=['POST'])
def create_job():
    try:
        data = request.json
        if not data.get('title') or not data.get('company'):
            return jsonify({'error': 'title and company are required'}), 400
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO jobs (title, company, location, salary_min, salary_max, description) VALUES (%s, %s, %s, %s, %s, %s)',
            (data['title'], data['company'], data.get('location'),
             data.get('salary_min'), data.get('salary_max'), data.get('description'))
        )
        db.commit()
        job_id = cursor.lastrowid
        cursor.close()
        db.close()
        logger.info(f'Created job id={job_id} title={data["title"]}')
        return jsonify({'id': job_id, 'status': 'created'}), 201
    except Exception as e:
        logger.error(f'Failed to create job: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM jobs WHERE id = %s', (job_id,))
        job = cursor.fetchone()
        cursor.close()
        db.close()
        if not job:
            return jsonify({'error': 'job not found'}), 404
        return jsonify(job), 200
    except Exception as e:
        logger.error(f'Failed to get job {job_id}: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/jobs/<int:job_id>/apply', methods=['POST'])
def apply(job_id):
    try:
        data = request.json
        if not data.get('email'):
            return jsonify({'error': 'email is required'}), 400
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO applications (job_id, candidate_email) VALUES (%s, %s)',
            (job_id, data['email'])
        )
        db.commit()
        app_id = cursor.lastrowid
        cursor.close()
        db.close()
        logger.info(f'Application id={app_id} for job_id={job_id}')
        return jsonify({'id': app_id, 'status': 'applied'}), 201
    except Exception as e:
        logger.error(f'Failed to apply for job {job_id}: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['GET'])
def stats():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT COUNT(*) as total_jobs FROM jobs')
        jobs = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) as total_applications FROM applications')
        apps = cursor.fetchone()
        cursor.close()
        db.close()
        return jsonify({
            'total_jobs': jobs['total_jobs'],
            'total_applications': apps['total_applications']
        }), 200
    except Exception as e:
        logger.error(f'Failed to get stats: {e}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
