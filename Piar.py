backend/
├── app.js
├── models/
│   └── Student.js
├── routes/
│   └── students.js
└── swagger.yaml
openapi: 3.0.0
info:
  title: API de Estudiantes con Necesidades Especiales
  version: 1.0.0
paths:
  /students:
    get:
      summary: Lista todos los estudiantes
      responses:
        '200':
          description: Lista de estudiantes
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Student'
    post:
      summary: Agrega un nuevo estudiante
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Student'
      responses:
        '201':
          description: Estudiante creado
  /students/{id}:
    get:
      summary: Obtiene un estudiante por ID
      parameters:
        - in: path
          name: id
          schema:
            type: string
          required: true
          description: ID del estudiante
      responses:
        '200':
          description: Estudiante
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Student'
        '404':
          description: Estudiante no encontrado
    put:
      summary: Actualiza un estudiante
      parameters:
        - in: path
          name: id
          schema:
            type: string
          required: true
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Student'
      responses:
        '200':
          description: Estudiante actualizado
        '404':
          description: Estudiante no encontrado
    delete:
      summary: Elimina un estudiante
      parameters:
        - in: path
          name: id
          schema:
            type: string
          required: true
      responses:
        '204':
          description: Estudiante eliminado
        '404':
          description: Estudiante no encontrado

components:
  schemas:
    Student:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        needs:
          type: string
        report:
          type: string
          const express = require('express');
const app = express();
const swaggerUi = require('swagger-ui-express');
const YAML = require('yamljs');

const swaggerDocument = YAML.load('./swagger.yaml');

app.use(express.json());

let students = [
  { id: '1', name: 'Juan Pérez', needs: 'TDAH', report: 'Informe 1' },
  { id: '2', name: 'María López', needs: 'Sordera', report: 'Informe 2' }
];

// Swagger UI
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// Endpoints
app.get('/students', (req, res) => {
  res.json(students);
});

app.post('/students', (req, res) => {
  const newStudent = { id: Date.now().toString(), ...req.body };
  students.push(newStudent);
  res.status(201).json(newStudent);
});

app.get('/students/:id', (req, res) => {
  const student = students.find(s => s.id === req.params.id);
  if (student) {
    res.json(student);
  } else {
    res.status(404).json({ message: 'Estudiante no encontrado' });
  }
});

app.put('/students/:id', (req, res) => {
  const index = students.findIndex(s => s.id === req.params.id);
  if (index !== -1) {
    students[index] = { ...students[index], ...req.body };
    res.json(students[index]);
  } else {
    res.status(404).json({ message: 'Estudiante no encontrado' });
  }
});

app.delete('/students/:id', (req, res) => {
  students = students.filter(s => s.id !== req.params.id);
  res.status(204).send();
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Servidor backend en puerto ${PORT}`);
});
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3001',
});

export default api;
import React, { createContext, useReducer } from 'react';

const initialState = {
  students: [],
  selectedStudent: null,
};

const reducer = (state, action) => {
  switch (action.type) {
    case 'SET_STUDENTS':
      return { ...state, students: action.payload };
    case 'ADD_STUDENT':
      return { ...state, students: [...state.students, action.payload] };
    case 'UPDATE_STUDENT':
      return {
        ...state,
        students: state.students.map(s =>
          s.id === action.payload.id ? action.payload : s
        ),
      };
    case 'DELETE_STUDENT':
      return {
        ...state,
        students: state.students.filter(s => s.id !== action.payload),
      };
    case 'SET_SELECTED':
      return { ...state, selectedStudent: action.payload };
    default:
      return state;
  }
};

export const StudentContext = createContext();

export const StudentProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <StudentContext.Provider value={{ state, dispatch }}>
      {children}
    </StudentContext.Provider>
  );
};
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import StudentList from './components/StudentList';
import StudentForm from './components/StudentForm';
import StudentReport from './components/StudentReport';

function App() {
  return (
    <Router>
      <nav>
        <Link to="/">Listado de Estudiantes</Link> |{' '}
        <Link to="/add">Agregar Estudiante</Link>
      </nav>
      <Routes>
        <Route path="/" element={<StudentList />} />
        <Route path="/add" element={<StudentForm />} />
        <Route path="/edit/:id" element={<StudentForm />} />
        <Route path="/report/:id" element={<StudentReport />} />
      </Routes>
    </Router>
  );
}

export default App;
import React, { useEffect, useContext } from 'react';
import api from '../services/api';
import { StudentContext } from '../context/StudentContext';
import { Link } from 'react-router-dom';

const StudentList = () => {
  const { state, dispatch } = useContext(StudentContext);

  useEffect(() => {
    api.get('/students').then(res => {
      dispatch({ type: 'SET_STUDENTS', payload: res.data });
    });
  }, []);

  const handleDelete = (id) => {
    api.delete(`/students/${id}`).then(() => {
      dispatch({ type: 'DELETE_STUDENT', payload: id });
    });
  };

  return (
    <div>
      <h2>Listado de Estudiantes</h2>
      <table border="1">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Necesidades</th>
            <th>Informe</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {state.students.map((student) => (
            <tr key={student.id}>
              <td>{student.name}</td>
              <td>{student.needs}</td>
              <td>{student.report}</td>
              <td>
                <Link to={`/edit/${student.id}`}>Editar</Link> |{' '}
                <button onClick={() => handleDelete(student.id)}>Eliminar</button> |{' '}
                <Link to={`/report/${student.id}`}>Ver Informe</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StudentList;
import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { StudentContext } from '../context/StudentContext';

const StudentForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { state, dispatch } = useContext(StudentContext);

  const [formData, setFormData] = useState({
    name: '',
    needs: '',
    report: '',
  });

  useEffect(() => {
    if (id) {
      // Editar
      api.get(`/students/${id}`).then(res => {
        setFormData(res.data);
        dispatch({ type: 'SET_SELECTED', payload: res.data });
      });
    }
  }, [id]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (id) {
      // Actualizar
      api.put(`/students/${id}`, formData).then((res) => {
        dispatch({ type: 'UPDATE_STUDENT', payload: res.data });
        navigate('/');
      });
    } else {
      // Crear
      api.post('/students', formData).then((res) => {
        dispatch({ type: 'ADD_STUDENT', payload: res.data });
        navigate('/');
      });
    }
  };

  return (
    <div>
      <h2>{id ? 'Editar Estudiante' : 'Agregar Estudiante'}</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Nombre:</label>
          <input
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Necesidades:</label>
          <input
            name="needs"
            value={formData.needs}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Informe:</label>
          <textarea
            name="report"
            value={formData.report}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit">{id ? 'Actualizar' : 'Guardar'}</button>
      </form>
    </div>
  );
};

export default StudentForm;
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';

const StudentReport = () => {
  const { id } = useParams();
  const [student, setStudent] = useState(null);

  useEffect(() => {
    api.get(`/students/${id}`).then(res => {
      setStudent(res.data);
    });
  }, [id]);

  if (!student) return <p>Cargando...</p>;

  return (
    <div>
      <h2>Informe de {student.name}</h2>
      <p><strong>Necesidades:</strong> {student.needs}</p>
      <p><strong>Informe:</strong> {student.report}</p>
    </div>
  );
};

export default StudentReport;
cd backend
npm init -y
npm install express swagger-ui-express yamljs
node app.js
# Servidor en http://localhost:3001
cd frontend
npx create-react-app .
npm install axios react-router-dom
npm start
# Servidor en http://localhost:3000