import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { adminApi } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import { RefreshCw, UserPlus, Edit2, Trash2, Clock, Bell, Calendar, Phone, User, Pause, Play } from 'lucide-react'

export default function OperatorsManagement() {
  const [operators, setOperators] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingOperator, setEditingOperator] = useState(null)
  const [newSchedule, setNewSchedule] = useState(null)
  const [editingSchedule, setEditingSchedule] = useState(null)
  const { toast } = useToast()

  const daysOfWeek = [
    { value: 0, label: 'Lunes' },
    { value: 1, label: 'Martes' },
    { value: 2, label: 'Miércoles' },
    { value: 3, label: 'Jueves' },
    { value: 4, label: 'Viernes' },
    { value: 5, label: 'Sábado' },
    { value: 6, label: 'Domingo' }
  ]

  const fetchOperators = async () => {
    try {
      setLoading(true)
      const response = await adminApi.getOperators()
      setOperators(response.data.operators || [])
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al cargar operadores',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOperators()
  }, [])

  const handleUpdateOperator = async (operatorData) => {
    try {
      await adminApi.updateOperator(operatorData.person_id, operatorData)
      toast({
        title: 'Operador Actualizado',
        description: 'Los datos del operador se actualizaron correctamente'
      })
      setEditingOperator(null)
      fetchOperators()
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al actualizar operador',
        variant: 'destructive'
      })
    }
  }

  const handleTogglePause = async (operator) => {
    try {
      if (operator.is_paused) {
        await adminApi.resumeOperator(operator.person_id)
        toast({
          title: 'Operador Reactivado',
          description: `${operator.name} ha sido reactivado`
        })
      } else {
        const reason = prompt('Motivo de la pausa:')
        if (reason) {
          await adminApi.pauseOperator(operator.person_id, reason)
          toast({
            title: 'Operador Pausado',
            description: `${operator.name} ha sido pausado`
          })
        }
      }
      fetchOperators()
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al cambiar estado del operador',
        variant: 'destructive'
      })
    }
  }

  const handleSaveSchedule = async (scheduleData, scheduleType) => {
    try {
      const data = {
        ...scheduleData,
        schedule_type: scheduleType,
        performed_by: 'admin'
      }
      
      if (editingSchedule) {
        await adminApi.updateSchedule(editingSchedule.id, data)
        toast({
          title: 'Horario Actualizado',
          description: `Horario de ${scheduleType === 'assignment' ? 'asignación' : 'alertas'} actualizado`
        })
      } else {
        await adminApi.createSchedule(data)
        toast({
          title: 'Horario Creado',
          description: `Horario de ${scheduleType === 'assignment' ? 'asignación' : 'alertas'} creado`
        })
      }
      
      setNewSchedule(null)
      setEditingSchedule(null)
      fetchOperators()
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al guardar horario',
        variant: 'destructive'
      })
    }
  }

  const handleDeleteSchedule = async (scheduleId) => {
    if (!confirm('¿Estás seguro de eliminar este horario?')) return
    
    try {
      await adminApi.deleteSchedule(scheduleId)
      toast({
        title: 'Horario Eliminado',
        description: 'El horario ha sido eliminado'
      })
      fetchOperators()
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al eliminar horario',
        variant: 'destructive'
      })
    }
  }

  const getDayName = (day) => {
    return daysOfWeek.find(d => d.value === day)?.label || 'Desconocido'
  }

  const groupSchedulesByDay = (schedules, type) => {
    const filtered = schedules.filter(s => s.schedule_type === type)
    const grouped = {}
    filtered.forEach(schedule => {
      if (!grouped[schedule.day_of_week]) {
        grouped[schedule.day_of_week] = []
      }
      grouped[schedule.day_of_week].push(schedule)
    })
    return grouped
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Gestión de Operadores</h1>
          <p className="text-muted-foreground">Administra operadores y sus horarios de asignación y alertas</p>
        </div>
        <Button onClick={fetchOperators}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualizar
        </Button>
      </div>

      <div className="space-y-4">
        {operators.map(operator => (
          <Card key={operator.person_id} className={
            operator.is_paused ? 'border-orange-300' :
            operator.is_active ? 'border-green-300' :
            'border-gray-300'
          }>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <User className="h-6 w-6" />
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {operator.name}
                      {operator.is_paused && <Badge variant="outline" className="bg-orange-100 text-orange-800">Pausado</Badge>}
                      {operator.is_active && !operator.is_paused && <Badge variant="outline" className="bg-green-100 text-green-800">Activo</Badge>}
                      {!operator.is_active && <Badge variant="outline" className="bg-gray-100 text-gray-800">Inactivo</Badge>}
                    </CardTitle>
                    <CardDescription>
                      Person ID: {operator.person_id} | WhatsApp: {operator.whatsapp_number || 'No configurado'} | Tickets: {operator.ticket_count || 0}
                    </CardDescription>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleTogglePause(operator)}
                  >
                    {operator.is_paused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
                  </Button>
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="outline" size="sm" onClick={() => setEditingOperator(operator)}>
                        <Edit2 className="h-4 w-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Editar Operador</DialogTitle>
                        <DialogDescription>Actualiza los datos del operador</DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <Label>Nombre</Label>
                          <Input
                            value={editingOperator?.name || ''}
                            onChange={(e) => setEditingOperator({...editingOperator, name: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label>Teléfono WhatsApp</Label>
                          <Input
                            value={editingOperator?.whatsapp_number || ''}
                            onChange={(e) => setEditingOperator({...editingOperator, whatsapp_number: e.target.value})}
                            placeholder="+1234567890"
                          />
                        </div>
                        <div className="flex items-center gap-2">
                          <Switch
                            checked={editingOperator?.is_active || false}
                            onCheckedChange={(checked) => setEditingOperator({...editingOperator, is_active: checked})}
                          />
                          <Label>Operador Activo</Label>
                        </div>
                        <div className="flex items-center gap-2">
                          <Switch
                            checked={editingOperator?.notifications_enabled || false}
                            onCheckedChange={(checked) => setEditingOperator({...editingOperator, notifications_enabled: checked})}
                          />
                          <Label>Notificaciones Habilitadas</Label>
                        </div>
                        <Button onClick={() => handleUpdateOperator(editingOperator)}>
                          Guardar Cambios
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="assignment" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="assignment" className="flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    Horarios de Asignación
                  </TabsTrigger>
                  <TabsTrigger value="alert" className="flex items-center gap-2">
                    <Bell className="h-4 w-4" />
                    Horarios de Alertas
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="assignment" className="space-y-4">
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-muted-foreground">Horarios para asignación de tickets</p>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button size="sm" onClick={() => setNewSchedule({ person_id: operator.person_id, type: 'assignment' })}>
                          <Clock className="h-4 w-4 mr-2" />
                          Agregar Horario
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Nuevo Horario de Asignación</DialogTitle>
                          <DialogDescription>Define cuándo este operador puede recibir tickets</DialogDescription>
                        </DialogHeader>
                        <ScheduleForm
                          schedule={newSchedule}
                          onChange={setNewSchedule}
                          onSave={(data) => handleSaveSchedule(data, 'assignment')}
                          onCancel={() => setNewSchedule(null)}
                          daysOfWeek={daysOfWeek}
                        />
                      </DialogContent>
                    </Dialog>
                  </div>
                  <ScheduleList
                    schedules={groupSchedulesByDay(operator.schedules || [], 'assignment')}
                    daysOfWeek={daysOfWeek}
                    onEdit={(schedule) => setEditingSchedule(schedule)}
                    onDelete={handleDeleteSchedule}
                  />
                </TabsContent>

                <TabsContent value="alert" className="space-y-4">
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-muted-foreground">Horarios para recibir notificaciones WhatsApp</p>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button size="sm" onClick={() => setNewSchedule({ person_id: operator.person_id, type: 'alert' })}>
                          <Bell className="h-4 w-4 mr-2" />
                          Agregar Horario
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Nuevo Horario de Alertas</DialogTitle>
                          <DialogDescription>Define cuándo este operador recibe notificaciones</DialogDescription>
                        </DialogHeader>
                        <ScheduleForm
                          schedule={newSchedule}
                          onChange={setNewSchedule}
                          onSave={(data) => handleSaveSchedule(data, 'alert')}
                          onCancel={() => setNewSchedule(null)}
                          daysOfWeek={daysOfWeek}
                        />
                      </DialogContent>
                    </Dialog>
                  </div>
                  <ScheduleList
                    schedules={groupSchedulesByDay(operator.schedules || [], 'alert')}
                    daysOfWeek={daysOfWeek}
                    onEdit={(schedule) => setEditingSchedule(schedule)}
                    onDelete={handleDeleteSchedule}
                  />
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

function ScheduleForm({ schedule, onChange, onSave, onCancel, daysOfWeek }) {
  return (
    <div className="space-y-4">
      <div>
        <Label>Día de la Semana</Label>
        <Select
          value={schedule?.day_of_week?.toString()}
          onValueChange={(value) => onChange({...schedule, day_of_week: parseInt(value)})}
        >
          <SelectTrigger>
            <SelectValue placeholder="Selecciona un día" />
          </SelectTrigger>
          <SelectContent>
            {daysOfWeek.map(day => (
              <SelectItem key={day.value} value={day.value.toString()}>
                {day.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label>Hora de Inicio</Label>
        <Input
          type="time"
          value={schedule?.start_time || ''}
          onChange={(e) => onChange({...schedule, start_time: e.target.value})}
        />
      </div>
      <div>
        <Label>Hora de Fin</Label>
        <Input
          type="time"
          value={schedule?.end_time || ''}
          onChange={(e) => onChange({...schedule, end_time: e.target.value})}
        />
      </div>
      <div className="flex gap-2">
        <Button onClick={() => onSave(schedule)}>Guardar</Button>
        <Button variant="outline" onClick={onCancel}>Cancelar</Button>
      </div>
    </div>
  )
}

function ScheduleList({ schedules, daysOfWeek, onEdit, onDelete }) {
  if (Object.keys(schedules).length === 0) {
    return (
      <p className="text-center text-muted-foreground py-4">
        No hay horarios configurados
      </p>
    )
  }

  return (
    <div className="space-y-2">
      {daysOfWeek.map(day => {
        const daySchedules = schedules[day.value] || []
        return (
          <div key={day.value} className="flex items-center justify-between py-2 border-b last:border-0">
            <span className="font-medium text-sm w-32">{day.label}</span>
            <div className="flex-1">
              {daySchedules.length > 0 ? (
                <div className="flex gap-2 flex-wrap">
                  {daySchedules.map(schedule => (
                    <div key={schedule.id} className="flex items-center gap-1">
                      <Badge variant="outline" className="bg-blue-100 text-blue-800">
                        {schedule.start_time} - {schedule.end_time}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                        onClick={() => onDelete(schedule.id)}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <span className="text-sm text-muted-foreground">Sin horario</span>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
