-- Execute this in the Supabase SQL Editor to RECREATE the tables for the MVP.
-- IMPORTANT: DROP existing tables first if they exist to avoid conflicts.
DROP TABLE IF EXISTS public.evidencias_alumnos CASCADE;
DROP TABLE IF EXISTS public.cuadernos_campo CASCADE;
DROP TABLE IF EXISTS public.evaluaciones CASCADE;
DROP TABLE IF EXISTS public.alumnos CASCADE;
DROP TABLE IF EXISTS public.docentes CASCADE;
DROP TABLE IF EXISTS public.aulas CASCADE;
DROP TABLE IF EXISTS public.areas CASCADE;

-- 1. ÁREAS
CREATE TABLE public.areas (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now(),
    nombre text NOT NULL UNIQUE
);
-- Pre-cargar áreas básicas
INSERT INTO public.areas (nombre) VALUES 
('Personal Social'), 
('Psicomotriz'), 
('Comunicación'), 
('Matemática'), 
('Ciencia y Tecnología')
ON CONFLICT DO NOTHING;

-- 2. AULAS
CREATE TABLE public.aulas (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now(),
    nombre text NOT NULL,
    edad int4 NOT NULL CHECK (edad IN (3, 4, 5))
);

-- 3. DOCENTES
CREATE TABLE public.docentes (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now(),
    nombre text NOT NULL,
    apellido text NOT NULL,
    id_aula uuid REFERENCES public.aulas(id) ON DELETE SET NULL,
    username text NOT NULL UNIQUE,
    password text NOT NULL,
    foto_perfil text
);

-- 4. ALUMNOS
CREATE TABLE public.alumnos (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now(),
    nombre text NOT NULL,
    apellido text NOT NULL,
    fecha_nacimiento date NOT NULL,
    id_aula uuid REFERENCES public.aulas(id) ON DELETE CASCADE,
    foto_perfil text
);

-- 5. CUADERNO DE CAMPO (CABECERA)
CREATE TABLE public.cuadernos_campo (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now(),
    id_docente uuid REFERENCES public.docentes(id) ON DELETE CASCADE,
    id_aula uuid REFERENCES public.aulas(id) ON DELETE CASCADE,
    titulo_actividad text NOT NULL,
    fecha date NOT NULL,
    id_area uuid REFERENCES public.areas(id) ON DELETE SET NULL,
    competencia text,
    estandar text,
    capacidades text,
    criterios text
);

-- 6. EVIDENCIAS DE ALUMNOS (DETALLE DEL CUADERNO)
CREATE TABLE public.evidencias_alumnos (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now(),
    id_cuaderno uuid REFERENCES public.cuadernos_campo(id) ON DELETE CASCADE,
    id_alumno uuid REFERENCES public.alumnos(id) ON DELETE CASCADE,
    descripcion text,
    retroalimentacion text
);

-- For MVP, disable RLS to allow direct access from Streamlit with Anon Key
ALTER TABLE public.areas DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.aulas DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.docentes DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.alumnos DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.cuadernos_campo DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidencias_alumnos DISABLE ROW LEVEL SECURITY;

-- 7. SESIONES DE CLASE
CREATE TABLE public.sesiones_clase (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now(),
    id_aula uuid REFERENCES public.aulas(id) ON DELETE CASCADE,
    fecha date NOT NULL,
    id_area uuid REFERENCES public.areas(id) ON DELETE SET NULL,
    UNIQUE(id_aula, fecha, id_area)
);

-- 8. ASISTENCIAS
CREATE TABLE public.asistencias (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now(),
    id_sesion uuid REFERENCES public.sesiones_clase(id) ON DELETE CASCADE,
    id_alumno uuid REFERENCES public.alumnos(id) ON DELETE CASCADE,
    asistio boolean DEFAULT true,
    UNIQUE(id_sesion, id_alumno)
);

ALTER TABLE public.sesiones_clase DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.asistencias DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidencias_alumnos DISABLE ROW LEVEL SECURITY;

-- 9. ASESORIAS IA
CREATE TABLE public.asesorias_ia (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamp with time zone DEFAULT now(),
    id_alumno uuid REFERENCES public.alumnos(id) ON DELETE CASCADE,
    id_docente uuid REFERENCES public.docentes(id) ON DELETE CASCADE,
    id_evidencia uuid REFERENCES public.evidencias_alumnos(id) ON DELETE CASCADE,
    asesoria_texto text NOT NULL,
    estado varchar(50) DEFAULT 'PENDIENTE'
);

ALTER TABLE public.asesorias_ia DISABLE ROW LEVEL SECURITY;
