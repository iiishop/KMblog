<template>
  <div class="CalendarPanel">
    <!-- 未展开模式 -->
    <div v-if="!isExpanded" class="compact-mode" @click="expand">
      <div class="month-header">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="icon">
          <path fill-rule="evenodd" d="M6.75 2.25A.75.75 0 0 1 7.5 3v1.5h9V3A.75.75 0 0 1 18 3v1.5h.75a3 3 0 0 1 3 3v11.25a3 3 0 0 1-3 3H5.25a3 3 0 0 1-3-3V7.5a3 3 0 0 1 3-3H6V3a.75.75 0 0 1 .75-.75Zm13.5 9a1.5 1.5 0 0 0-1.5-1.5H5.25a1.5 1.5 0 0 0-1.5 1.5v7.5a1.5 1.5 0 0 0 1.5 1.5h13.5a1.5 1.5 0 0 0 1.5-1.5v-7.5Z" clip-rule="evenodd" />
        </svg>
        <span class="month-title">{{ currentMonthYear }}</span>
      </div>

      <div class="mini-calendar">
        <div class="weekday-row">
          <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
        </div>
        <div class="days-grid">
          <div
            v-for="day in calendarDays"
            :key="day.date"
            class="mini-day"
            :class="{
              'other-month': !day.isCurrentMonth,
              'today': day.isToday,
              'has-events': day.events.length > 0
            }"
          >
            <span class="day-num">{{ day.day }}</span>
            <span v-if="day.events.length > 0" class="event-dot"></span>
          </div>
        </div>
      </div>

      <div class="today-summary">
        <div class="summary-label">今日事件</div>
        <div class="summary-value">{{ todayEvents.length }}</div>
      </div>
    </div>

    <!-- 展开模式 - 使用 Teleport -->
    <Teleport to="body">
      <div v-if="isExpanded" class="calendar-expanded-wrapper">
        <div class="calendar-overlay" @click="collapse"></div>
        <div class="calendar-expanded-panel">
          <div class="expanded-header">
            <h2>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path fill-rule="evenodd" d="M6.75 2.25A.75.75 0 0 1 7.5 3v1.5h9V3A.75.75 0 0 1 18 3v1.5h.75a3 3 0 0 1 3 3v11.25a3 3 0 0 1-3 3H5.25a3 3 0 0 1-3-3V7.5a3 3 0 0 1 3-3H6V3a.75.75 0 0 1 .75-.75Zm13.5 9a1.5 1.5 0 0 0-1.5-1.5H5.25a1.5 1.5 0 0 0-1.5 1.5v7.5a1.5 1.5 0 0 0 1.5 1.5h13.5a1.5 1.5 0 0 0 1.5-1.5v-7.5Z" clip-rule="evenodd" />
              </svg>
              日历与日程
            </h2>
            <button class="close-btn" @click="collapse">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path fill-rule="evenodd" d="M5.47 5.47a.75.75 0 0 1 1.06 0L12 10.94l5.47-5.47a.75.75 0 1 1 1.06 1.06L13.06 12l5.47 5.47a.75.75 0 1 1-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 0 1-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>

          <div class="expanded-content">
            <div class="week-timeline">
              <div class="timeline-header">
                <button class="nav-btn" @click="previousWeek">‹</button>
                <span class="week-range">{{ weekRangeText }}</span>
                <button class="nav-btn" @click="nextWeek">›</button>
              </div>
              <div class="timeline-grid">
                <div class="time-column">
                  <div class="time-header"></div>
                  <div v-for="hour in 24" :key="hour" class="time-label">
                    {{ String(hour - 1).padStart(2, '0') }}:00
                  </div>
                </div>
                <div
                  v-for="day in weekDays"
                  :key="day.date"
                  class="day-column"
                  :class="{ 'is-today': day.isToday }"
                >
                  <div class="day-header">
                    <div class="day-name">{{ day.weekday }}</div>
                    <div class="day-date">{{ day.dayMonth }}</div>
                    <div v-if="day.events.length > 0" class="day-count">{{ day.events.length }}</div>
                  </div>
                  <div class="day-timeline">
                    <div v-for="hour in 24" :key="hour" class="hour-slot"></div>
                    <div
                      v-for="event in day.events"
                      :key="event.id"
                      class="timeline-event"
                      :style="getEventStyle(event)"
                    >
                      <div class="event-time">{{ formatEventTime(event) }}</div>
                      <div class="event-title">{{ event.title }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="month-calendar">
              <div class="calendar-nav">
                <button @click="previousMonth">‹</button>
                <span class="calendar-month">{{ currentMonthYear }}</span>
                <button @click="nextMonth">›</button>
              </div>
              <div class="calendar-grid">
                <div v-for="day in weekdays" :key="day" class="calendar-weekday">{{ day }}</div>
                <div
                  v-for="day in calendarDays"
                  :key="day.date"
                  class="calendar-day"
                  :class="{
                    'other-month': !day.isCurrentMonth,
                    'today': day.isToday,
                    'has-events': day.events.length > 0,
                    'selected': day.date === selectedDate
                  }"
                  @click="selectDay(day)"
                >
                  <span class="day-number">{{ day.day }}</span>
                  <div v-if="day.events.length > 0" class="event-indicators">
                    <span
                      v-for="(event, idx) in day.events.slice(0, 3)"
                      :key="idx"
                      class="event-dot"
                      :style="{ backgroundColor: event.color }"
                    ></span>
                  </div>
                </div>
              </div>
              <div v-if="selectedDayData" class="selected-day-events">
                <h3>{{ selectedDayData.dateFormatted }}</h3>
                <div class="events-list">
                  <div v-for="event in selectedDayData.events" :key="event.id" class="event-item">
                    <span class="event-color" :style="{ backgroundColor: event.color }"></span>
                    <div class="event-info">
                      <div class="event-name">{{ event.title }}</div>
                      <div class="event-time-range">{{ event.timeRange }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
export default {
  name: 'CalendarPanel',
  data() {
    return {
      isExpanded: false,
      currentDate: new Date(),
      currentWeekStart: null,
      selectedDate: null,
      events: [],
      weekdays: ['日', '一', '二', '三', '四', '五', '六']
    }
  },
  computed: {
    todayEvents() {
      const today = this.formatDate(new Date())
      return this.events.filter(event => this.isEventOnDate(event, today))
    },
    currentMonthYear() {
      return `${this.currentDate.getFullYear()}年${this.currentDate.getMonth() + 1}月`
    },
    weekRangeText() {
      if (!this.currentWeekStart) return ''
      const start = new Date(this.currentWeekStart)
      const end = new Date(start)
      end.setDate(end.getDate() + 6)
      return `${start.getMonth() + 1}/${start.getDate()} - ${end.getMonth() + 1}/${end.getDate()}`
    },
    weekDays() {
      if (!this.currentWeekStart) return []
      const days = []
      const weekdayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      for (let i = 0; i < 7; i++) {
        const date = new Date(this.currentWeekStart)
        date.setDate(date.getDate() + i)
        const dateStr = this.formatDate(date)
        days.push({
          date: dateStr,
          weekday: weekdayNames[date.getDay()],
          dayMonth: `${date.getMonth() + 1}/${date.getDate()}`,
          isToday: dateStr === this.formatDate(new Date()),
          events: this.getEventsForDate(dateStr)
        })
      }
      return days
    },
    calendarDays() {
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      const firstDayWeek = firstDay.getDay()
      const daysInMonth = lastDay.getDate()
      const days = []
      const today = this.formatDate(new Date())
      const prevMonthLastDay = new Date(year, month, 0).getDate()
      for (let i = firstDayWeek - 1; i >= 0; i--) {
        const day = prevMonthLastDay - i
        const date = this.formatDate(new Date(year, month - 1, day))
        days.push({ day, date, isCurrentMonth: false, isToday: false, events: this.getEventsForDate(date) })
      }
      for (let day = 1; day <= daysInMonth; day++) {
        const date = this.formatDate(new Date(year, month, day))
        days.push({ day, date, isCurrentMonth: true, isToday: date === today, events: this.getEventsForDate(date) })
      }
      const remainingDays = 42 - days.length
      for (let day = 1; day <= remainingDays; day++) {
        const date = this.formatDate(new Date(year, month + 1, day))
        days.push({ day, date, isCurrentMonth: false, isToday: false, events: this.getEventsForDate(date) })
      }
      return days
    },
    selectedDayData() {
      if (!this.selectedDate) return null
      const events = this.getEventsForDate(this.selectedDate)
      const date = new Date(this.selectedDate)
      return {
        dateFormatted: `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`,
        events
      }
    }
  },
  methods: {
    formatDate(date) {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },
    isEventOnDate(event, dateStr) {
      const eventStart = new Date(event.startDate)
      const eventEnd = new Date(event.endDate)
      const checkDate = new Date(dateStr)
      return checkDate >= new Date(eventStart.toDateString()) && checkDate <= new Date(eventEnd.toDateString())
    },
    getEventsForDate(dateStr) {
      const events = this.events.filter(event => this.isEventOnDate(event, dateStr))
      return events.map(event => {
        const eventStart = new Date(event.startDate)
        const eventEnd = new Date(event.endDate)
        return {
          ...event,
          timeRange: this.formatTimeRange(eventStart, eventEnd)
        }
      })
    },
    formatTimeRange(start, end) {
      const formatTime = (date) => {
        const hours = date.getHours()
        const minutes = date.getMinutes()
        if (hours === 0 && minutes === 0) return ''
        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
      }
      const startTime = formatTime(start)
      const endTime = formatTime(end)
      if (this.formatDate(start) === this.formatDate(end)) {
        if (startTime && endTime) return `${startTime} - ${endTime}`
        return '全天'
      }
      return `${this.formatDate(start)} - ${this.formatDate(end)}`
    },
    formatEventTime(event) {
      const start = new Date(event.startDate)
      const hours = start.getHours()
      const minutes = start.getMinutes()
      if (hours === 0 && minutes === 0) return '全天'
      return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
    },
    getEventStyle(event) {
      const start = new Date(event.startDate)
      const startMinutes = start.getHours() * 60 + start.getMinutes()
      const top = (startMinutes / (24 * 60)) * 100
      return {
        top: `${top}%`,
        height: '5%',
        backgroundColor: event.color,
        borderLeft: `3px solid ${event.color}`
      }
    },
    getWeekStart(date) {
      const d = new Date(date)
      const day = d.getDay()
      const diff = d.getDate() - day
      return new Date(d.setDate(diff))
    },
    expand() {
      this.isExpanded = true
      if (!this.selectedDate) this.selectedDate = this.formatDate(new Date())
      if (!this.currentWeekStart) this.currentWeekStart = this.getWeekStart(new Date())
    },
    collapse() {
      this.isExpanded = false
    },
    selectDay(day) {
      this.selectedDate = day.date
    },
    previousMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1, 1)
    },
    nextMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 1)
    },
    previousWeek() {
      const newStart = new Date(this.currentWeekStart)
      newStart.setDate(newStart.getDate() - 7)
      this.currentWeekStart = newStart
    },
    nextWeek() {
      const newStart = new Date(this.currentWeekStart)
      newStart.setDate(newStart.getDate() + 7)
      this.currentWeekStart = newStart
    },
    async loadEvents() {
      this.events = [
        {
          id: '1',
          title: '示例事件',
          startDate: new Date().toISOString(),
          endDate: new Date().toISOString(),
          color: '#4ade80'
        }
      ]
    }
  },
  mounted() {
    this.loadEvents()
    this.currentWeekStart = this.getWeekStart(new Date())
  }
}
</script>

<style scoped>
/* 基础面板 */
.CalendarPanel {
  background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
  width: 100%;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  color: #e5e5e5;
  border: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  overflow: hidden;
}

.CalendarPanel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #4ade80, #2a2a2a, #4ade80);
}

/* 紧凑模式 */
.compact-mode {
  padding: 1.25rem;
  cursor: pointer;
}

.month-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(74, 222, 128, 0.2);
}

.month-header .icon {
  width: 24px;
  height: 24px;
  color: #4ade80;
}

.month-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #4ade80;
  font-family: 'Orbitron', monospace;
}

.mini-calendar {
  margin-bottom: 1rem;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 4px;
}

.weekday {
  text-align: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(74, 222, 128, 0.6);
  padding: 4px 0;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.mini-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  font-size: 0.85rem;
  position: relative;
}

.mini-day.other-month {
  opacity: 0.3;
}

.mini-day.today {
  background: rgba(74, 222, 128, 0.2);
  border: 1px solid #4ade80;
  color: #4ade80;
  font-weight: 700;
}

.event-dot {
  position: absolute;
  bottom: 2px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #4ade80;
  box-shadow: 0 0 4px rgba(74, 222, 128, 0.8);
}

.today-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: rgba(74, 222, 128, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(74, 222, 128, 0.3);
}

.summary-label {
  font-size: 0.9rem;
  color: rgba(74, 222, 128, 0.8);
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #4ade80;
  font-family: 'Orbitron', monospace;
}

/* 展开模式 */
.calendar-expanded-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.calendar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
}

.calendar-expanded-panel {
  position: relative;
  width: 95%;
  max-width: 1400px;
  height: 90vh;
  background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1;
}

.expanded-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(74, 222, 128, 0.2);
  background: linear-gradient(145deg, #2f2f2f, #252525);
  flex-shrink: 0;
}

.expanded-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #4ade80;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.expanded-header h2 svg {
  width: 28px;
  height: 28px;
}

.close-btn {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 12px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #ef4444;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  transform: scale(1.1);
}

.close-btn svg {
  width: 20px;
  height: 20px;
}

.expanded-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 1.5rem;
  padding: 1.5rem 2rem;
  overflow: hidden;
  min-height: 0;
}

/* 一周时间轴 */
.week-timeline {
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 16px;
  padding: 1rem;
  overflow: hidden;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(74, 222, 128, 0.2);
}

.week-range {
  font-size: 1.1rem;
  font-weight: 700;
  color: #4ade80;
  font-family: 'Orbitron', monospace;
}

.nav-btn {
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.3);
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #4ade80;
  font-size: 1.2rem;
}

.nav-btn:hover {
  background: rgba(74, 222, 128, 0.2);
}

.timeline-grid {
  display: grid;
  grid-template-columns: 60px repeat(7, 1fr);
  gap: 8px;
  overflow-y: auto;
  max-height: calc(90vh - 200px);
}

.time-column {
  display: flex;
  flex-direction: column;
}

.time-header {
  height: 60px;
  flex-shrink: 0;
}

.time-label {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  font-size: 0.75rem;
  color: rgba(74, 222, 128, 0.6);
  font-family: 'SF Mono', monospace;
}

.day-column {
  display: flex;
  flex-direction: column;
  min-width: 100px;
}

.day-column.is-today {
  background: rgba(74, 222, 128, 0.05);
  border-radius: 8px;
}

.day-header {
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 8px;
  margin-bottom: 8px;
  flex-shrink: 0;
  position: relative;
}

.day-column.is-today .day-header {
  background: rgba(74, 222, 128, 0.2);
  border: 1px solid #4ade80;
}

.day-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: rgba(74, 222, 128, 0.8);
}

.day-date {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
}

.day-count {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #4ade80;
  color: #0a1a0f;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
}

.day-timeline {
  position: relative;
  flex: 1;
}

.hour-slot {
  height: 60px;
  border-bottom: 1px solid rgba(74, 222, 128, 0.1);
}

.timeline-event {
  position: absolute;
  left: 4px;
  right: 4px;
  border-radius: 6px;
  padding: 4px 6px;
  font-size: 0.75rem;
  color: white;
  overflow: hidden;
  cursor: pointer;
}

.event-time {
  font-weight: 700;
  font-size: 0.7rem;
}

.event-title {
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 月历 */
.month-calendar {
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 16px;
  padding: 1rem;
  overflow-y: auto;
}

.calendar-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(74, 222, 128, 0.2);
}

.calendar-nav button {
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.3);
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #4ade80;
  font-size: 1.2rem;
}

.calendar-month {
  font-size: 1rem;
  font-weight: 700;
  color: #4ade80;
  font-family: 'Orbitron', monospace;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
  margin-bottom: 1rem;
}

.calendar-weekday {
  text-align: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(74, 222, 128, 0.6);
  padding: 6px 0;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  padding: 4px;
}

.calendar-day:hover {
  background: rgba(74, 222, 128, 0.1);
  border-color: rgba(74, 222, 128, 0.3);
}

.calendar-day.other-month {
  opacity: 0.3;
}

.calendar-day.today {
  background: rgba(74, 222, 128, 0.2);
  border-color: #4ade80;
  font-weight: 700;
}

.calendar-day.selected {
  background: rgba(74, 222, 128, 0.3);
  border-color: #4ade80;
}

.day-number {
  font-size: 0.9rem;
}

.event-indicators {
  display: flex;
  gap: 2px;
  margin-top: 2px;
}

.event-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
}

.selected-day-events {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(74, 222, 128, 0.2);
}

.selected-day-events h3 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #4ade80;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 8px;
}

.event-color {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.event-info {
  flex: 1;
}

.event-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #e5e5e5;
}

.event-time-range {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
}

@media (max-width: 1200px) {
  .expanded-content {
    grid-template-columns: 1fr;
  }
}
</style>
