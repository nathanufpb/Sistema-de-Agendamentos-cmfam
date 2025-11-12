"""
Sistema de Agendamentos - CMFAM/UEPB
Flask application for laboratory equipment scheduling
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'

DATABASE = 'agendamentos.db'

def get_db_connection():
    """Establish database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create equipment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            localizacao TEXT,
            ativo BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            tipo TEXT DEFAULT 'usuario',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create reservations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipamento_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            data_inicio TIMESTAMP NOT NULL,
            data_fim TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pendente',
            observacoes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (equipamento_id) REFERENCES equipamentos (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute('SELECT COUNT(*) FROM equipamentos')
    if cursor.fetchone()[0] == 0:
        sample_equipment = [
            ('Microscópio Eletrônico', 'Microscópio de varredura eletrônica (MEV)', 'Sala 101'),
            ('Termocicladora PCR', 'Termocicladora para PCR em tempo real', 'Sala 102'),
            ('Termocicladora extração', 'Termocicladora para extração de DNA', 'Sala 103'),
            ('Analisador Térmico', 'Analisador termogravimétrico (TGA)', 'Sala 104')
        ]
        cursor.executemany(
            'INSERT INTO equipamentos (nome, descricao, localizacao) VALUES (?, ?, ?)',
            sample_equipment
        )
    
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ('Admin Sistema', 'admin@uepb.edu.br', 'admin'),
            ('João Silva', 'joao.silva@uepb.edu.br', 'usuario'),
            ('Maria Santos', 'maria.santos@uepb.edu.br', 'usuario')
        ]
        cursor.executemany(
            'INSERT INTO usuarios (nome, email, tipo) VALUES (?, ?, ?)',
            sample_users
        )
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Main dashboard page"""
    conn = get_db_connection()
    equipamentos = conn.execute('SELECT * FROM equipamentos WHERE ativo = 1').fetchall()
    
    # Get today's reservations
    hoje = datetime.now().strftime('%Y-%m-%d')
    reservas_hoje = conn.execute('''
        SELECT r.*, e.nome as equipamento_nome, u.nome as usuario_nome
        FROM reservas r
        JOIN equipamentos e ON r.equipamento_id = e.id
        JOIN usuarios u ON r.usuario_id = u.id
        WHERE date(r.data_inicio) = ?
        ORDER BY r.data_inicio
    ''', (hoje,)).fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                         equipamentos=equipamentos,
                         reservas_hoje=reservas_hoje)

@app.route('/equipamentos')
def equipamentos():
    """List all equipment"""
    conn = get_db_connection()
    equipamentos = conn.execute('SELECT * FROM equipamentos ORDER BY nome').fetchall()
    conn.close()
    return render_template('equipamentos.html', equipamentos=equipamentos)

@app.route('/equipamento/<int:id>')
def equipamento_detalhes(id):
    """Show equipment details and reservations"""
    conn = get_db_connection()
    equipamento = conn.execute('SELECT * FROM equipamentos WHERE id = ?', (id,)).fetchone()
    
    if not equipamento:
        flash('Equipamento não encontrado', 'error')
        return redirect(url_for('equipamentos'))
    
    # Get upcoming reservations for this equipment
    reservas = conn.execute('''
        SELECT r.*, u.nome as usuario_nome, u.email as usuario_email
        FROM reservas r
        JOIN usuarios u ON r.usuario_id = u.id
        WHERE r.equipamento_id = ? AND r.data_fim >= datetime('now')
        ORDER BY r.data_inicio
    ''', (id,)).fetchall()
    
    conn.close()
    return render_template('equipamento_detalhes.html', 
                         equipamento=equipamento,
                         reservas=reservas)

@app.route('/reservar', methods=['GET', 'POST'])
def reservar():
    """Create new reservation"""
    if request.method == 'POST':
        equipamento_id = request.form.get('equipamento_id')
        usuario_id = request.form.get('usuario_id')
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        observacoes = request.form.get('observacoes', '')
        
        # Validate inputs
        if not all([equipamento_id, usuario_id, data_inicio, data_fim]):
            flash('Todos os campos obrigatórios devem ser preenchidos', 'error')
            return redirect(url_for('reservar'))
        
        # Check for conflicts
        conn = get_db_connection()
        conflitos = conn.execute('''
            SELECT COUNT(*) as count FROM reservas
            WHERE equipamento_id = ?
            AND status != 'cancelada'
            AND (
                (data_inicio <= ? AND data_fim > ?) OR
                (data_inicio < ? AND data_fim >= ?) OR
                (data_inicio >= ? AND data_fim <= ?)
            )
        ''', (equipamento_id, data_inicio, data_inicio, data_fim, data_fim, data_inicio, data_fim)).fetchone()
        
        if conflitos['count'] > 0:
            flash('Conflito de horário! Já existe uma reserva neste período.', 'error')
            conn.close()
            return redirect(url_for('reservar'))
        
        # Create reservation
        conn.execute('''
            INSERT INTO reservas (equipamento_id, usuario_id, data_inicio, data_fim, observacoes, status)
            VALUES (?, ?, ?, ?, ?, 'confirmada')
        ''', (equipamento_id, usuario_id, data_inicio, data_fim, observacoes))
        
        conn.commit()
        conn.close()
        
        flash('Reserva criada com sucesso!', 'success')
        return redirect(url_for('minhas_reservas'))
    
    # GET request - show form
    conn = get_db_connection()
    equipamentos = conn.execute('SELECT * FROM equipamentos WHERE ativo = 1 ORDER BY nome').fetchall()
    usuarios = conn.execute('SELECT * FROM usuarios ORDER BY nome').fetchall()
    conn.close()
    
    return render_template('reservar.html', 
                         equipamentos=equipamentos,
                         usuarios=usuarios)

@app.route('/minhas-reservas')
def minhas_reservas():
    """Show user's reservations (simplified - shows all for demo)"""
    conn = get_db_connection()
    reservas = conn.execute('''
        SELECT r.*, e.nome as equipamento_nome, u.nome as usuario_nome
        FROM reservas r
        JOIN equipamentos e ON r.equipamento_id = e.id
        JOIN usuarios u ON r.usuario_id = u.id
        ORDER BY r.data_inicio DESC
    ''').fetchall()
    conn.close()
    
    return render_template('minhas_reservas.html', reservas=reservas)

@app.route('/cancelar-reserva/<int:id>', methods=['POST'])
def cancelar_reserva(id):
    """Cancel a reservation"""
    conn = get_db_connection()
    conn.execute('''
        UPDATE reservas SET status = 'cancelada'
        WHERE id = ?
    ''', (id,))
    conn.commit()
    conn.close()
    
    flash('Reserva cancelada com sucesso!', 'success')
    return redirect(url_for('minhas_reservas'))

@app.route('/api/reservas/<int:equipamento_id>')
def api_reservas_equipamento(equipamento_id):
    """API endpoint to get reservations for an equipment (for calendar view)"""
    conn = get_db_connection()
    reservas = conn.execute('''
        SELECT r.id, r.data_inicio, r.data_fim, r.status, u.nome as usuario_nome
        FROM reservas r
        JOIN usuarios u ON r.usuario_id = u.id
        WHERE r.equipamento_id = ? AND r.status != 'cancelada'
        ORDER BY r.data_inicio
    ''', (equipamento_id,)).fetchall()
    conn.close()
    
    # Convert to list of dicts
    reservas_list = []
    for r in reservas:
        reservas_list.append({
            'id': r['id'],
            'title': f"{r['usuario_nome']} ({r['status']})",
            'start': r['data_inicio'],
            'end': r['data_fim'],
            'status': r['status']
        })
    
    return jsonify(reservas_list)

@app.route('/calendario')
def calendario():
    """Calendar view of all reservations"""
    conn = get_db_connection()
    equipamentos = conn.execute('SELECT * FROM equipamentos WHERE ativo = 1 ORDER BY nome').fetchall()
    conn.close()
    return render_template('calendario.html', equipamentos=equipamentos)

@app.route('/admin')
def admin():
    """Admin panel for managing equipment and users"""
    conn = get_db_connection()
    equipamentos = conn.execute('SELECT * FROM equipamentos ORDER BY nome').fetchall()
    usuarios = conn.execute('SELECT * FROM usuarios ORDER BY nome').fetchall()
    
    # Statistics
    total_reservas = conn.execute('SELECT COUNT(*) as count FROM reservas').fetchone()['count']
    reservas_ativas = conn.execute(
        "SELECT COUNT(*) as count FROM reservas WHERE status = 'confirmada'"
    ).fetchone()['count']
    
    conn.close()
    
    return render_template('admin.html',
                         equipamentos=equipamentos,
                         usuarios=usuarios,
                         total_reservas=total_reservas,
                         reservas_ativas=reservas_ativas)

@app.route('/admin/equipamentos/criar', methods=['POST'])
def criar_equipamento():
    """Handle creation of a new equipment record"""
    nome = (request.form.get('nome') or '').strip()
    descricao = (request.form.get('descricao') or '').strip()
    localizacao = (request.form.get('localizacao') or '').strip()
    ativo = 1 if request.form.get('ativo') == 'on' else 0

    if not nome:
        flash('O nome do equipamento é obrigatório.', 'error')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO equipamentos (nome, descricao, localizacao, ativo) VALUES (?, ?, ?, ?)',
        (nome, descricao, localizacao, ativo)
    )
    conn.commit()
    conn.close()

    flash('Equipamento cadastrado com sucesso!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/equipamentos/<int:equipamento_id>/editar', methods=['POST'])
def editar_equipamento(equipamento_id):
    """Update equipment information"""
    nome = (request.form.get('nome') or '').strip()
    descricao = (request.form.get('descricao') or '').strip()
    localizacao = (request.form.get('localizacao') or '').strip()
    ativo = 1 if request.form.get('ativo') == 'on' else 0

    if not nome:
        flash('O nome do equipamento é obrigatório.', 'error')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    cursor = conn.execute(
        '''
        UPDATE equipamentos
        SET nome = ?, descricao = ?, localizacao = ?, ativo = ?
        WHERE id = ?
        ''',
        (nome, descricao, localizacao, ativo, equipamento_id)
    )
    updated = cursor.rowcount
    conn.commit()
    conn.close()

    if updated == 0:
        flash('Equipamento não encontrado.', 'error')
    else:
        flash('Equipamento atualizado com sucesso!', 'success')

    return redirect(url_for('admin'))

@app.route('/admin/equipamentos/<int:equipamento_id>/status', methods=['POST'])
def alterar_status_equipamento(equipamento_id):
    """Toggle equipment active status"""
    try:
        novo_status = int(request.form.get('ativo', '1'))
    except ValueError:
        flash('Status inválido informado.', 'error')
        return redirect(url_for('admin'))

    if novo_status not in (0, 1):
        flash('Status inválido informado.', 'error')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    cursor = conn.execute(
        'UPDATE equipamentos SET ativo = ? WHERE id = ?',
        (novo_status, equipamento_id)
    )
    updated = cursor.rowcount
    conn.commit()
    conn.close()

    if updated == 0:
        flash('Equipamento não encontrado.', 'error')
    else:
        status_label = 'ativado' if novo_status == 1 else 'desativado'
        flash(f'Equipamento {status_label} com sucesso!', 'success')

    return redirect(url_for('admin'))

@app.route('/admin/usuarios/criar', methods=['POST'])
def criar_usuario():
    """Handle creation of a new user account"""
    nome = (request.form.get('nome') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    tipo = (request.form.get('tipo') or 'usuario').strip().lower()

    if not nome or not email:
        flash('Nome e e-mail são obrigatórios.', 'error')
        return redirect(url_for('admin'))

    if tipo not in ('admin', 'usuario'):
        tipo = 'usuario'

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO usuarios (nome, email, tipo) VALUES (?, ?, ?)',
            (nome, email, tipo)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        flash('Já existe um usuário cadastrado com este e-mail.', 'error')
    else:
        flash('Usuário cadastrado com sucesso!', 'success')
    finally:
        conn.close()

    return redirect(url_for('admin'))

@app.route('/admin/usuarios/<int:usuario_id>/editar', methods=['POST'])
def editar_usuario(usuario_id):
    """Update user details"""
    nome = (request.form.get('nome') or '').strip()
    email = (request.form.get('email') or '').strip().lower()
    tipo = (request.form.get('tipo') or 'usuario').strip().lower()

    if not nome or not email:
        flash('Nome e e-mail são obrigatórios.', 'error')
        return redirect(url_for('admin'))

    if tipo not in ('admin', 'usuario'):
        tipo = 'usuario'

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            'UPDATE usuarios SET nome = ?, email = ?, tipo = ? WHERE id = ?',
            (nome, email, tipo, usuario_id)
        )
        updated = cursor.rowcount
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        flash('Já existe um usuário cadastrado com este e-mail.', 'error')
        return redirect(url_for('admin'))

    conn.close()

    if updated == 0:
        flash('Usuário não encontrado.', 'error')
    else:
        flash('Usuário atualizado com sucesso!', 'success')

    return redirect(url_for('admin'))

if __name__ == '__main__':
    # Initialize database
    if not os.path.exists(DATABASE):
        init_db()
    
    # Run the app
    # Note: For production, set debug=False and use a production WSGI server
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
