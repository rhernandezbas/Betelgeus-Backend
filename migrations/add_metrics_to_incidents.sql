-- Migración: Agregar campos de métricas a tickets_detection
-- Fecha: 2026-01-15
-- Objetivo: Unificar lógica de tickets moviendo campos de ticket_response_metrics a tickets_detection

-- Agregar columnas de métricas
ALTER TABLE tickets_detection 
ADD COLUMN IF NOT EXISTS exceeded_threshold BOOLEAN DEFAULT FALSE COMMENT 'Si el ticket supera el threshold (>60 min)',
ADD COLUMN IF NOT EXISTS response_time_minutes INT DEFAULT NULL COMMENT 'Tiempo de respuesta en minutos',
ADD COLUMN IF NOT EXISTS first_alert_sent_at DATETIME DEFAULT NULL COMMENT 'Primera alerta enviada',
ADD COLUMN IF NOT EXISTS last_alert_sent_at DATETIME DEFAULT NULL COMMENT 'Última alerta enviada';

-- Migrar datos existentes de ticket_response_metrics a tickets_detection
UPDATE tickets_detection td
INNER JOIN ticket_response_metrics trm ON td.Ticket_ID = trm.ticket_id
SET 
    td.exceeded_threshold = trm.exceeded_threshold,
    td.response_time_minutes = trm.response_time_minutes,
    td.first_alert_sent_at = trm.first_alert_sent_at,
    td.last_alert_sent_at = trm.last_alert_sent_at
WHERE trm.ticket_id IS NOT NULL;

-- Verificar migración
SELECT 
    COUNT(*) as total_tickets,
    SUM(CASE WHEN exceeded_threshold = TRUE THEN 1 ELSE 0 END) as exceeded_count,
    SUM(CASE WHEN response_time_minutes IS NOT NULL THEN 1 ELSE 0 END) as with_response_time
FROM tickets_detection;
