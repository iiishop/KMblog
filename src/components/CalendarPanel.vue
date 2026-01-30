<template>
  <div class="CalendarPanel">
    <!-- 未展开模式 -->
    <div v-if="!isExpanded" class="compact-mode" @click="expand">
      <div class="month-header">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="icon">
          <path fill-rule="evenodd"
            d="M6.75 2.25A.75.75 0 0 1 7.5 3v1.5h9V3A.75.75 0 0 1 18 3v1.5h.75a3 3 0 0 1 3 3v11.25a3 3 0 0 1-3 3H5.25a3 3 0 0 1-3-3V7.5a3 3 0 0 1 3-3H6V3a.75.75 0 0 1 .75-.75Zm13.5 9a1.5 1.5 0 0 0-1.5-1.5H5.25a1.5 1.5 0 0 0-1.5 1.5v7.5a1.5 1.5 0 0 0 1.5 1.5h13.5a1.5 1.5 0 0 0 1.5-1.5v-7.5Z"
            clip-rule="evenodd" />
        </svg>
        <span class="month-title">{{ currentMonthYear }}</span>
      </div>

      <div class="mini-calendar">
        <div class="weekday-row">
          <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
        </div>
        <div class="days-grid">
          <div v-for="day in calendarDays" :key="day.date" class="mini-day" :class="{
            'other-month': !day.isCurrentMonth,
            'today': day.isToday,
            'has-events': day.events.length > 0
          }">
            <span class="day-num">{{ day.day }}</span>
            <div v-if="day.events.length > 0" class="event-bars">
              <div v-for="(event, idx) in day.events" :key="idx" class="event-bar" :style="{
                backgroundColor: event.color,
                width: `${100 / day.events.length}%`
              }" :title="event.title"></div>
            </div>
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
      <div v-if="isExpanded" class="calendar-expanded-wrapper" @click.self="collapse">
        <div class="calendar-expanded-panel" @click.stop>
          <div class="expanded-header">
            <h2>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path fill-rule="evenodd"
                  d="M6.75 2.25A.75.75 0 0 1 7.5 3v1.5h9V3A.75.75 0 0 1 18 3v1.5h.75a3 3 0 0 1 3 3v11.25a3 3 0 0 1-3 3H5.25a3 3 0 0 1-3-3V7.5a3 3 0 0 1 3-3H6V3a.75.75 0 0 1 .75-.75Zm13.5 9a1.5 1.5 0 0 0-1.5-1.5H5.25a1.5 1.5 0 0 0-1.5 1.5v7.5a1.5 1.5 0 0 0 1.5 1.5h13.5a1.5 1.5 0 0 0 1.5-1.5v-7.5Z"
                  clip-rule="evenodd" />
              </svg>
              日历与日程
            </h2>
            <button class="close-btn" @click="collapse">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path fill-rule="evenodd"
                  d="M5.47 5.47a.75.75 0 0 1 1.06 0L12 10.94l5.47-5.47a.75.75 0 1 1 1.06 1.06L13.06 12l5.47 5.47a.75.75 0 1 1-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 0 1-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 0 1 0-1.06Z"
                  clip-rule="evenodd" />
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
                <div v-for="day in weekDays" :key="day.date" class="day-column" :class="{ 'is-today': day.isToday }">
                  <div class="day-header">
                    <div class="day-name">{{ day.weekday }}</div>
                    <div class="day-date">{{ day.dayMonth }}</div>
                    <div v-if="day.eventCount > 0" class="day-count">{{ day.eventCount }}</div>
                  </div>
                  <div class="day-timeline">
                    <div v-for="hour in 24" :key="hour" class="hour-slot"></div>
                    <div v-for="event in day.events" :key="event.id" class="timeline-event" :class="{
                      'event-continuing': event.isContinuing,
                      'event-first-day': event.isFirstDay,
                      'event-last-day': event.isLastDay,
                      'event-segmented': event.isSegmented,
                      'event-auto-scheduled': event.isAutoScheduled,
                      'event-conflict': event.hasConflict
                    }" :style="getEventStyle(event)" @click="navigateToArticle(event)" :title="getEventTooltip(event)">
                      <div class="event-time">
                        <span v-if="event.isFirstDay && !event.isSegmented">{{ formatEventTime(event) }}</span>
                        <span v-else-if="event.isContinuing">继续</span>
                        <span v-else-if="event.isLastDay">结束</span>
                      </div>
                      <div class="event-title">{{ event.title }}</div>
                      <div v-if="event.duration > 1 && !event.isSegmented" class="event-duration">{{ event.duration }}天
                      </div>
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
                <div v-for="day in calendarDays" :key="day.date" class="calendar-day" :class="{
                  'other-month': !day.isCurrentMonth,
                  'today': day.isToday,
                  'has-events': day.events.length > 0,
                  'selected': day.date === selectedDate
                }" @click="selectDay(day)">
                  <span class="day-number">{{ day.day }}</span>
                  <div v-if="day.events.length > 0" class="event-indicators">
                    <span v-for="(event, idx) in day.events.slice(0, 3)" :key="idx" class="event-dot"
                      :style="{ backgroundColor: event.color }"></span>
                  </div>
                </div>
              </div>
              <div v-if="selectedDayData" class="selected-day-events">
                <h3>{{ selectedDayData.dateFormatted }}</h3>
                <div class="events-list">
                  <div v-for="event in selectedDayData.events" :key="event.id" class="event-item"
                    @click="navigateToArticle(event)">
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
import { useRouter } from 'vue-router'

export default {
  name: 'CalendarPanel',
  setup() {
    const router = useRouter()
    return { router }
  },
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
      return this.getUniqueEventsForDate(today)
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
        const uniqueEvents = this.getUniqueEventsForDate(dateStr)
        days.push({
          date: dateStr,
          weekday: weekdayNames[date.getDay()],
          dayMonth: `${date.getMonth() + 1}/${date.getDate()}`,
          isToday: dateStr === this.formatDate(new Date()),
          events: this.getEventsForDate(dateStr), // 时间轴需要完整的分段事件
          eventCount: uniqueEvents.length // 但计数使用去重后的
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

      // 上个月的日期
      for (let i = firstDayWeek - 1; i >= 0; i--) {
        const day = prevMonthLastDay - i
        const date = this.formatDate(new Date(year, month - 1, day))
        const events = this.getUniqueEventsForDate(date)
        days.push({ day, date, isCurrentMonth: false, isToday: false, events })
      }

      // 当前月的日期
      for (let day = 1; day <= daysInMonth; day++) {
        const date = this.formatDate(new Date(year, month, day))
        const events = this.getUniqueEventsForDate(date)
        days.push({ day, date, isCurrentMonth: true, isToday: date === today, events })
      }

      // 下个月的日期
      const remainingDays = 42 - days.length
      for (let day = 1; day <= remainingDays; day++) {
        const date = this.formatDate(new Date(year, month + 1, day))
        const events = this.getUniqueEventsForDate(date)
        days.push({ day, date, isCurrentMonth: false, isToday: false, events })
      }

      return days
    },
    selectedDayData() {
      if (!this.selectedDate) return null
      const events = this.getEventsForDate(this.selectedDate)

      // 合并分段事件：如果多个事件有相同的原始ID（去掉-segment-X后缀），只保留一个
      const uniqueEvents = []
      const seenIds = new Set()

      events.forEach(event => {
        // 提取原始ID（移除 -segment-X 后缀）
        const originalId = event.id.replace(/-segment-\d+$/, '')

        if (!seenIds.has(originalId)) {
          seenIds.add(originalId)
          // 使用原始事件数据（不是分段后的）
          const originalEvent = event.isSegmented
            ? { ...event, id: originalId }
            : event
          uniqueEvents.push(originalEvent)
        }
      })

      const date = new Date(this.selectedDate)
      return {
        dateFormatted: `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`,
        events: uniqueEvents
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

      // 为每个事件添加额外信息
      const enrichedEvents = events.map(event => {
        const eventStart = new Date(event.startDate)
        const eventEnd = new Date(event.endDate)
        const checkDate = new Date(dateStr)

        // 判断是否是事件的第一天
        const isFirstDay = this.formatDate(eventStart) === dateStr
        // 判断是否是事件的最后一天
        const isLastDay = this.formatDate(eventEnd) === dateStr

        return {
          ...event,
          timeRange: this.formatTimeRange(eventStart, eventEnd),
          isFirstDay,
          isLastDay,
          isContinuing: !isFirstDay && !isLastDay
        }
      })

      // 计算事件的布局位置（避免重叠）
      return this.calculateEventLayout(enrichedEvents, dateStr)
    },
    getUniqueEventsForDate(dateStr) {
      const events = this.getEventsForDate(dateStr)

      // 合并分段事件
      const uniqueEvents = []
      const seenIds = new Set()

      events.forEach(event => {
        const originalId = event.id.replace(/-segment-\d+$/, '')
        if (!seenIds.has(originalId)) {
          seenIds.add(originalId)
          uniqueEvents.push(event)
        }
      })

      return uniqueEvents
    },
    calculateEventLayout(events, dateStr) {
      if (events.length === 0) return events

      const checkDate = new Date(dateStr)
      const dayStart = new Date(checkDate.setHours(0, 0, 0, 0))
      const dayEnd = new Date(checkDate.setHours(23, 59, 59, 999))

      // 按优先级分类事件
      const timedEvents = events.filter(e => e.eventType === 'timed')
      const timeRangedAllDayEvents = events.filter(e => e.eventType === 'time-ranged-allday')
      const durationAllDayEvents = events.filter(e => e.eventType === 'duration-allday')
      const regularAllDayEvents = events.filter(e => e.eventType === 'regular-allday')

      // 1. 处理时间段事件（不再需要预先计算列，动态宽度会处理）
      const layoutTimedEvents = timedEvents.map(e => ({
        ...e,
        isAllDay: false
      }))

      // 2. 处理有时间范围的全天事件（被时间段事件截断）
      const layoutTimeRangedEvents = []
      timeRangedAllDayEvents.forEach((event, idx) => {
        const eventStart = new Date(event.startDate)
        const eventEnd = new Date(event.endDate)
        const totalDuration = (eventEnd - eventStart) / (1000 * 60) // 分钟

        // 找到与此事件重叠的时间段事件
        const overlappingTimed = layoutTimedEvents.filter(te => {
          const teStart = new Date(te.startDate)
          const teEnd = new Date(te.endDate)
          return teStart < eventEnd && teEnd > eventStart
        })

        if (overlappingTimed.length === 0) {
          // 没有重叠，正常显示
          layoutTimeRangedEvents.push({
            ...event,
            columnIndex: idx,
            totalColumns: timeRangedAllDayEvents.length,
            isAllDay: true
          })
        } else {
          // 有重叠，需要截断并保持总时长
          const segments = []
          let currentStart = eventStart
          let remainingDuration = totalDuration

          // 按时间排序重叠事件
          const sortedOverlapping = overlappingTimed
            .map(e => ({ start: new Date(e.startDate), end: new Date(e.endDate) }))
            .sort((a, b) => a.start - b.start)

          sortedOverlapping.forEach(overlap => {
            if (currentStart < overlap.start && remainingDuration > 0) {
              const segmentEnd = new Date(Math.min(overlap.start, eventEnd))
              const segmentDuration = (segmentEnd - currentStart) / (1000 * 60)

              segments.push({
                startDate: currentStart.toISOString(),
                endDate: segmentEnd.toISOString()
              })

              remainingDuration -= segmentDuration
            }
            currentStart = new Date(Math.max(currentStart, overlap.end))
          })

          // 如果还有剩余时长，添加到最后
          if (remainingDuration > 0 && currentStart < dayEnd) {
            const finalEnd = new Date(Math.min(currentStart.getTime() + remainingDuration * 60 * 1000, dayEnd))
            segments.push({
              startDate: currentStart.toISOString(),
              endDate: finalEnd.toISOString()
            })
          }

          segments.forEach((segment, segIdx) => {
            layoutTimeRangedEvents.push({
              ...event,
              id: `${event.id}-segment-${segIdx}`,
              startDate: segment.startDate,
              endDate: segment.endDate,
              columnIndex: idx,
              totalColumns: timeRangedAllDayEvents.length,
              isAllDay: true,
              isSegmented: true,
              segmentIndex: segIdx,
              totalSegments: segments.length
            })
          })
        }
      })

      // 3. 自动调度有时长的全天事件
      const layoutDurationEvents = this.autoScheduleEvents(
        durationAllDayEvents,
        dateStr,
        [...layoutTimedEvents, ...layoutTimeRangedEvents]
      )

      // 4. 处理普通全天事件（被所有其他事件截断）
      const layoutRegularAllDayEvents = []
      regularAllDayEvents.forEach((event, idx) => {
        const allOtherEvents = [...layoutTimedEvents, ...layoutTimeRangedEvents, ...layoutDurationEvents]

        const overlapping = allOtherEvents.filter(e => {
          const eStart = new Date(e.startDate)
          const eEnd = new Date(e.endDate)
          return eStart < dayEnd && eEnd > dayStart
        })

        if (overlapping.length === 0) {
          layoutRegularAllDayEvents.push({
            ...event,
            columnIndex: idx,
            totalColumns: regularAllDayEvents.length,
            isAllDay: true
          })
        } else {
          const segments = []
          let currentStart = dayStart

          const sortedOverlapping = overlapping
            .map(e => ({ start: new Date(e.startDate), end: new Date(e.endDate) }))
            .sort((a, b) => a.start - b.start)

          sortedOverlapping.forEach(overlap => {
            if (currentStart < overlap.start) {
              segments.push({
                startDate: currentStart.toISOString(),
                endDate: overlap.start.toISOString()
              })
            }
            currentStart = new Date(Math.max(currentStart, overlap.end))
          })

          if (currentStart < dayEnd) {
            segments.push({
              startDate: currentStart.toISOString(),
              endDate: dayEnd.toISOString()
            })
          }

          segments.forEach((segment, segIdx) => {
            layoutRegularAllDayEvents.push({
              ...event,
              id: `${event.id}-segment-${segIdx}`,
              startDate: segment.startDate,
              endDate: segment.endDate,
              columnIndex: idx,
              totalColumns: regularAllDayEvents.length,
              isAllDay: true,
              isSegmented: true,
              segmentIndex: segIdx,
              totalSegments: segments.length
            })
          })
        }
      })

      // 合并所有事件
      const allEvents = [...layoutTimedEvents, ...layoutTimeRangedEvents, ...layoutDurationEvents, ...layoutRegularAllDayEvents]

      // 应用动态宽度算法：只在重叠时分配列宽
      return this.applyDynamicWidth(allEvents)
    },

    // 应用动态宽度：所有事件默认全宽，只在重叠区域按比例分配
    applyDynamicWidth(events) {
      if (events.length === 0) return []

      // 按开始时间排序
      const sortedEvents = events
        .map(e => ({
          ...e,
          start: new Date(e.startDate),
          end: new Date(e.endDate)
        }))
        .sort((a, b) => a.start - b.start || a.end - b.end)

      // 为每个事件计算动态布局段
      const result = []

      sortedEvents.forEach(event => {
        // 找到所有与此事件重叠的其他事件
        const overlappingEvents = sortedEvents.filter(other =>
          other !== event &&
          other.start < event.end &&
          other.end > event.start
        )

        if (overlappingEvents.length === 0) {
          // 没有重叠，整个事件占满宽度
          result.push({
            ...event,
            columnIndex: 0,
            totalColumns: 1
          })
        } else {
          // 创建时间点列表（所有重叠事件的开始和结束时间）
          const timePoints = new Set([event.start.getTime(), event.end.getTime()])
          overlappingEvents.forEach(other => {
            if (other.start > event.start && other.start < event.end) {
              timePoints.add(other.start.getTime())
            }
            if (other.end > event.start && other.end < event.end) {
              timePoints.add(other.end.getTime())
            }
          })

          const sortedTimePoints = Array.from(timePoints).sort((a, b) => a - b)

          // 为每个时间段计算重叠数量和列位置
          for (let i = 0; i < sortedTimePoints.length - 1; i++) {
            const segmentStart = new Date(sortedTimePoints[i])
            const segmentEnd = new Date(sortedTimePoints[i + 1])

            // 找到在这个时间段内重叠的所有事件
            const overlappingInSegment = sortedEvents.filter(e =>
              e.start < segmentEnd && e.end > segmentStart
            )

            // 找到当前事件在重叠列表中的索引
            const columnIndex = overlappingInSegment.findIndex(e => e.id === event.id)
            const totalColumns = overlappingInSegment.length

            result.push({
              ...event,
              id: `${event.id}-dyn-${i}`,
              startDate: segmentStart.toISOString(),
              endDate: segmentEnd.toISOString(),
              columnIndex,
              totalColumns,
              isDynamicSegment: sortedTimePoints.length > 2,
              dynamicSegmentIndex: i,
              totalDynamicSegments: sortedTimePoints.length - 1
            })
          }
        }
      })

      return result
    },

    // 自动调度有时长的全天事件
    autoScheduleEvents(events, dateStr, existingEvents) {
      if (events.length === 0) return []

      const checkDate = new Date(dateStr)

      // 计算起床和睡觉时间
      let wakeTime = 8 // 默认8点起床
      let sleepTime = 24 // 默认24点睡觉

      existingEvents.forEach(e => {
        const start = new Date(e.startDate)
        const end = new Date(e.endDate)
        const startHour = start.getHours() + start.getMinutes() / 60
        const endHour = end.getHours() + end.getMinutes() / 60

        if (startHour < wakeTime) wakeTime = Math.floor(startHour)
        if (endHour > sleepTime) sleepTime = Math.ceil(endHour)
      })

      // 创建时间槽（以30分钟为单位）
      const slots = []
      for (let hour = wakeTime; hour < sleepTime; hour++) {
        for (let half = 0; half < 2; half++) {
          const slotStart = new Date(checkDate)
          slotStart.setHours(hour, half * 30, 0, 0)
          const slotEnd = new Date(slotStart)
          slotEnd.setMinutes(slotEnd.getMinutes() + 30)

          // 检查是否被占用
          const isOccupied = existingEvents.some(e => {
            const eStart = new Date(e.startDate)
            const eEnd = new Date(e.endDate)
            return eStart < slotEnd && eEnd > slotStart
          })

          slots.push({ start: slotStart, end: slotEnd, occupied: isOccupied })
        }
      }

      // 为每个事件分配时间
      const scheduledEvents = []

      events.forEach((event, idx) => {
        const durationHours = event.durationHours || 1
        const slotsNeeded = Math.ceil(durationHours * 2) // 每小时2个槽

        // 找到连续的空闲槽
        let bestStart = -1
        let consecutiveFree = 0

        for (let i = 0; i < slots.length; i++) {
          if (!slots[i].occupied) {
            if (consecutiveFree === 0) bestStart = i
            consecutiveFree++

            if (consecutiveFree >= slotsNeeded) {
              // 找到足够的空间，标记为占用
              for (let j = bestStart; j < bestStart + slotsNeeded; j++) {
                slots[j].occupied = true
              }

              scheduledEvents.push({
                ...event,
                startDate: slots[bestStart].start.toISOString(),
                endDate: slots[bestStart + slotsNeeded - 1].end.toISOString(),
                columnIndex: idx,
                totalColumns: events.length,
                isAllDay: false,
                isAutoScheduled: true
              })

              break
            }
          } else {
            consecutiveFree = 0
            bestStart = -1
          }
        }

        // 如果找不到空间，强制放置（会重叠）
        if (bestStart === -1 || consecutiveFree < slotsNeeded) {
          const fallbackStart = new Date(checkDate)
          fallbackStart.setHours(wakeTime, 0, 0, 0)
          const fallbackEnd = new Date(fallbackStart)
          fallbackEnd.setHours(fallbackEnd.getHours() + durationHours)

          scheduledEvents.push({
            ...event,
            startDate: fallbackStart.toISOString(),
            endDate: fallbackEnd.toISOString(),
            columnIndex: idx,
            totalColumns: events.length,
            isAllDay: false,
            isAutoScheduled: true,
            hasConflict: true
          })
        }
      })

      return scheduledEvents
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

      const end = new Date(event.endDate)
      const durationMinutes = (end - start) / (1000 * 60)

      const isSameDay = this.formatDate(start) === this.formatDate(end)
      let height

      if (isSameDay) {
        height = Math.max((durationMinutes / (24 * 60)) * 100, 3)
      } else {
        const endOfDay = new Date(start)
        endOfDay.setHours(23, 59, 59)
        const minutesToEndOfDay = (endOfDay - start) / (1000 * 60)
        height = (minutesToEndOfDay / (24 * 60)) * 100
      }

      const totalColumns = event.totalColumns || 1
      const columnIndex = event.columnIndex || 0
      const width = 100 / totalColumns
      const left = (width * columnIndex)

      // 为自动调度的事件添加特殊样式
      let borderStyle = `3px solid ${event.color}`
      if (event.isAutoScheduled) {
        borderStyle = `3px dashed ${event.color}`
      }
      if (event.hasConflict) {
        borderStyle = `3px dotted ${event.color}`
      }

      return {
        top: `${top}%`,
        height: `${height}%`,
        left: `${left}%`,
        width: `${width - 1}%`,
        backgroundColor: event.color,
        borderLeft: borderStyle,
        opacity: event.hasConflict ? 0.7 : 1
      }
    },
    getEventTooltip(event) {
      let tooltip = `${event.title}`
      if (event.section) tooltip += ` - ${event.section}`
      tooltip += `\n${event.timeRange}`

      if (event.isSegmented) {
        tooltip += `\n(片段 ${event.segmentIndex + 1}/${event.totalSegments})`
      }

      if (event.isAutoScheduled) {
        tooltip += `\n⏰ 自动调度 (${event.durationHours}小时)`
      }

      if (event.hasConflict) {
        tooltip += `\n⚠️ 时间冲突`
      }

      const typeLabels = {
        'timed': '时间段事件',
        'time-ranged-allday': '固定时间全天事件',
        'duration-allday': '时长全天事件',
        'regular-allday': '普通全天事件'
      }

      if (event.eventType) {
        tooltip += `\n类型: ${typeLabels[event.eventType] || event.eventType}`
      }

      return tooltip
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
      // 同时更新左侧时间轴到该日期所在的周
      const selectedDateObj = new Date(day.date)
      this.currentWeekStart = this.getWeekStart(selectedDateObj)
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
    navigateToArticle(event) {
      if (!event.articlePath) {
        console.warn('事件缺少 articlePath:', event)
        return
      }

      console.log('导航到文章:', event.articlePath)

      // 解析文章路径，例如: /Posts/Markdowns/Calendar-Example.md
      const pathMatch = event.articlePath.match(/\/Posts\/(.+)\/(.+)\.md$/)
      if (pathMatch) {
        const [, collection, mdName] = pathMatch

        // 如果是 Markdowns 目录，不需要 collection 参数
        if (collection === 'Markdowns') {
          this.router.push({ name: 'PostPage', params: { mdName } })
        } else {
          this.router.push({ name: 'PostPage', params: { collection, mdName } })
        }
      } else {
        console.warn('无法解析文章路径:', event.articlePath)
      }
    },
    parseMermaidGantt(content, articlePath, articleDate) {
      const events = []
      const ganttBlocks = content.match(/```mermaid\s*gantt[\s\S]*?```/g)

      if (!ganttBlocks) return events

      // 解析文章日期作为默认年份
      let defaultYear = new Date().getFullYear()
      let defaultMonth = new Date().getMonth() + 1
      let defaultDay = new Date().getDate()

      if (articleDate) {
        const parsedDate = new Date(articleDate)
        if (!isNaN(parsedDate.getTime())) {
          defaultYear = parsedDate.getFullYear()
          defaultMonth = parsedDate.getMonth() + 1
          defaultDay = parsedDate.getDate()
        }
      }

      ganttBlocks.forEach((block, blockIndex) => {
        const lines = block.split('\n').slice(1, -1)
        let dateFormat = 'YYYY-MM-DD'
        let currentSection = ''
        let sectionTimeRange = null
        let sectionDuration = null
        let eventId = 0

        // 智能日期解析函数
        const parseSmartDate = (dateStr, isEndDate = false, startDateObj = null) => {
          if (!dateStr) return null

          // 如果已经是完整的 ISO 格式，直接解析
          if (dateStr.match(/^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2})?/)) {
            return dateStr
          }

          // 处理只有时间的情况 (HH:MM)
          if (dateStr.match(/^\d{1,2}:\d{2}$/)) {
            const baseDate = startDateObj ? new Date(startDateObj) : new Date(defaultYear, defaultMonth - 1, defaultDay)
            return `${baseDate.getFullYear()}-${String(baseDate.getMonth() + 1).padStart(2, '0')}-${String(baseDate.getDate()).padStart(2, '0')}T${dateStr.padStart(5, '0')}`
          }

          // 处理只有月日的情况 (MM-DD 或 M-D)
          if (dateStr.match(/^\d{1,2}-\d{1,2}$/)) {
            const [month, day] = dateStr.split('-').map(n => parseInt(n))
            let year = defaultYear

            // 如果是结束日期且月份小于开始日期的月份，说明跨年了
            if (isEndDate && startDateObj) {
              const startDate = new Date(startDateObj)
              const startMonth = startDate.getMonth() + 1
              if (month < startMonth) {
                year = startDate.getFullYear() + 1
              } else {
                year = startDate.getFullYear()
              }
            }

            return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
          }

          // 处理只有月日和时间的情况 (MM-DD HH:MM)
          if (dateStr.match(/^\d{1,2}-\d{1,2}\s+\d{1,2}:\d{2}$/)) {
            const [datePart, timePart] = dateStr.split(/\s+/)
            const [month, day] = datePart.split('-').map(n => parseInt(n))
            let year = defaultYear

            if (isEndDate && startDateObj) {
              const startDate = new Date(startDateObj)
              const startMonth = startDate.getMonth() + 1
              if (month < startMonth) {
                year = startDate.getFullYear() + 1
              } else {
                year = startDate.getFullYear()
              }
            }

            return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T${timePart.padStart(5, '0')}`
          }

          // 默认返回原始字符串
          return dateStr
        }

        lines.forEach(line => {
          line = line.trim()

          if (line.startsWith('dateFormat')) {
            dateFormat = line.split(/\s+/)[1]
          }

          else if (line.startsWith('section')) {
            currentSection = line.substring(7).trim()

            // 检查时间范围 (HH:MM-HH:MM)
            const timeRangeMatch = currentSection.match(/\((\d{1,2}:\d{2})-(\d{1,2}:\d{2})\)/i)
            if (timeRangeMatch) {
              sectionTimeRange = {
                startTime: timeRangeMatch[1].padStart(5, '0'),
                endTime: timeRangeMatch[2].padStart(5, '0')
              }
              sectionDuration = null
            }
            // 检查时长 (3h)
            else {
              const durationMatch = currentSection.match(/\((\d+(?:\.\d+)?)\s*h\)/i)
              if (durationMatch) {
                sectionDuration = parseFloat(durationMatch[1])
                sectionTimeRange = null
              } else {
                sectionTimeRange = null
                sectionDuration = null
              }
            }
          }

          else if (line && !line.startsWith('title') && !line.startsWith('gantt')) {
            const taskMatch = line.match(/^(.+?)\s*:(.*)$/)
            if (taskMatch) {
              const [, title, taskData] = taskMatch
              const parts = taskData.split(',').map(p => p.trim())

              let status = ''
              let taskId = ''
              let startDate = null
              let endDate = null
              let duration = null

              parts.forEach(part => {
                if (['done', 'active', 'crit', 'milestone'].includes(part)) {
                  status = part
                } else if (!taskId && !part.match(/^\d{4}-\d{2}-\d{2}/)) {
                  taskId = part
                } else if (part.match(/^\d{4}-\d{2}-\d{2}/) || part.match(/^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}/)) {
                  if (!startDate) {
                    startDate = part
                  } else if (!endDate) {
                    endDate = part
                  }
                } else if (part.match(/^\d+d$/)) {
                  duration = parseInt(part)
                }
              })

              if (startDate) {
                try {
                  let color = '#4ade80'
                  if (status === 'done') color = '#10b981'
                  else if (status === 'active') color = '#3b82f6'
                  else if (status === 'crit') color = '#ef4444'
                  else if (status === 'milestone') color = '#f59e0b'

                  // 使用智能日期解析
                  const parsedStartDate = parseSmartDate(startDate, false)
                  const parsedEndDate = endDate ? parseSmartDate(endDate, true, parsedStartDate) : null

                  // 处理有时间范围的全天事件
                  if (sectionTimeRange && parsedEndDate) {
                    const rangeStart = new Date(parsedStartDate + 'T00:00:00')
                    const rangeEnd = new Date(parsedEndDate + 'T23:59:59')
                    const daysDiff = Math.ceil((rangeEnd - rangeStart) / (1000 * 60 * 60 * 24))

                    if (daysDiff > 1) {
                      const currentDate = new Date(rangeStart)
                      while (currentDate <= rangeEnd) {
                        const dateStr = currentDate.toISOString().split('T')[0]
                        const dayStart = new Date(`${dateStr}T${sectionTimeRange.startTime}:00`)
                        const dayEnd = new Date(`${dateStr}T${sectionTimeRange.endTime}:00`)

                        events.push({
                          id: `${articlePath}-${blockIndex}-${eventId++}`,
                          title: title.trim(),
                          section: currentSection,
                          startDate: dayStart.toISOString(),
                          endDate: dayEnd.toISOString(),
                          status,
                          color,
                          articlePath,
                          duration: 1,
                          eventType: 'time-ranged-allday',
                          priority: 2
                        })

                        currentDate.setDate(currentDate.getDate() + 1)
                      }
                      return
                    }
                  }

                  // 处理有时长的全天事件
                  if (sectionDuration && parsedEndDate) {
                    const rangeStart = new Date(parsedStartDate + 'T00:00:00')
                    const rangeEnd = new Date(parsedEndDate + 'T23:59:59')
                    const daysDiff = Math.ceil((rangeEnd - rangeStart) / (1000 * 60 * 60 * 24))

                    if (daysDiff > 1) {
                      const currentDate = new Date(rangeStart)
                      while (currentDate <= rangeEnd) {
                        const dateStr = currentDate.toISOString().split('T')[0]

                        events.push({
                          id: `${articlePath}-${blockIndex}-${eventId++}`,
                          title: title.trim(),
                          section: currentSection,
                          startDate: new Date(`${dateStr}T00:00:00`).toISOString(),
                          endDate: new Date(`${dateStr}T23:59:59`).toISOString(),
                          status,
                          color,
                          articlePath,
                          duration: 1,
                          eventType: 'duration-allday',
                          durationHours: sectionDuration,
                          priority: 3,
                          needsScheduling: true
                        })

                        currentDate.setDate(currentDate.getDate() + 1)
                      }
                      return
                    }
                  }

                  // 普通事件处理
                  let start, end

                  if (dateFormat.includes('HH:mm') || parsedStartDate.includes('T')) {
                    start = new Date(parsedStartDate)
                  } else {
                    start = new Date(parsedStartDate + 'T00:00:00')
                  }

                  if (parsedEndDate) {
                    if (dateFormat.includes('HH:mm') || parsedEndDate.includes('T')) {
                      end = new Date(parsedEndDate)
                    } else {
                      end = new Date(parsedEndDate + 'T23:59:59')
                    }
                  } else if (duration) {
                    end = new Date(start)
                    end.setDate(end.getDate() + duration)
                  } else {
                    end = new Date(start)
                    if (!dateFormat.includes('HH:mm') && !parsedStartDate.includes('T')) {
                      end.setHours(23, 59, 59)
                    } else {
                      end = new Date(start)
                      end.setHours(end.getHours() + 1)
                    }
                  }

                  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
                    console.warn(`无效的日期: ${startDate} - ${endDate}`)
                    return
                  }

                  const durationDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24))

                  // 判断事件类型
                  const startHour = start.getHours()
                  const endHour = end.getHours()
                  const startMinute = start.getMinutes()
                  const endMinute = end.getMinutes()
                  const isAllDay = (startHour === 0 && startMinute === 0 && endHour === 23 && endMinute === 59) ||
                    ((end - start) / (1000 * 60 * 60) > 20)

                  // 如果是全天事件且没有时间范围或时长标记，默认当作5小时的全天事件
                  if (isAllDay && !sectionTimeRange && !sectionDuration) {
                    // 如果跨越多天，为每一天创建5小时的事件
                    if (durationDays > 1) {
                      const currentDate = new Date(start)
                      while (currentDate <= end) {
                        const dateStr = currentDate.toISOString().split('T')[0]

                        events.push({
                          id: `${articlePath}-${blockIndex}-${eventId++}`,
                          title: title.trim(),
                          section: currentSection,
                          startDate: new Date(`${dateStr}T00:00:00`).toISOString(),
                          endDate: new Date(`${dateStr}T23:59:59`).toISOString(),
                          status,
                          color,
                          articlePath,
                          duration: 1,
                          eventType: 'duration-allday',
                          durationHours: 5,
                          priority: 3,
                          needsScheduling: true
                        })

                        currentDate.setDate(currentDate.getDate() + 1)
                      }
                      return
                    } else {
                      // 单天的全天事件，也当作5小时
                      events.push({
                        id: `${articlePath}-${blockIndex}-${eventId++}`,
                        title: title.trim(),
                        section: currentSection,
                        startDate: start.toISOString(),
                        endDate: end.toISOString(),
                        status,
                        color,
                        articlePath,
                        duration: 1,
                        eventType: 'duration-allday',
                        durationHours: 5,
                        priority: 3,
                        needsScheduling: true
                      })
                      return
                    }
                  }

                  events.push({
                    id: `${articlePath}-${blockIndex}-${eventId++}`,
                    title: title.trim(),
                    section: currentSection,
                    startDate: start.toISOString(),
                    endDate: end.toISOString(),
                    status,
                    color,
                    articlePath,
                    duration: Math.max(1, durationDays),
                    eventType: isAllDay ? 'regular-allday' : 'timed',
                    priority: isAllDay ? 4 : 1
                  })
                } catch (error) {
                  console.warn(`解析日期失败: ${startDate}`, error)
                }
              }
            }
          }
        })
      })

      return events
    },
    async loadEvents() {
      try {
        // 获取所有 markdown 文件列表
        const response = await fetch('/assets/PostDirectory.json')
        const postDirectory = await response.json()

        const allEvents = []
        const allPaths = []

        // 收集所有文章路径
        const collectPaths = (obj) => {
          if (Array.isArray(obj)) {
            obj.forEach(item => {
              if (item.path) allPaths.push(item.path)
            })
          } else if (typeof obj === 'object') {
            Object.values(obj).forEach(value => collectPaths(value))
          }
        }

        collectPaths(postDirectory)

        console.log(`找到 ${allPaths.length} 篇文章`)

        // 遍历所有文章
        for (const path of allPaths) {
          try {
            // 读取文章内容
            const contentResponse = await fetch(path)
            if (!contentResponse.ok) continue

            const content = await contentResponse.text()

            // 从 frontmatter 提取日期
            const dateMatch = content.match(/^---\s*\n[\s\S]*?date:\s*(.+?)\n[\s\S]*?---/)
            const articleDate = dateMatch ? dateMatch[1].trim() : null

            // 解析 Mermaid Gantt
            const events = this.parseMermaidGantt(content, path, articleDate)
            if (events.length > 0) {
              console.log(`从 ${path} 解析到 ${events.length} 个事件`)
              allEvents.push(...events)
            }
          } catch (error) {
            console.warn(`无法加载文章 ${path}:`, error)
          }
        }

        this.events = allEvents
        console.log(`✅ 成功加载 ${allEvents.length} 个日历事件`)
      } catch (error) {
        console.error('❌ 加载日历事件失败:', error)
        this.events = []
      }
    }
  },
  mounted() {
    this.loadEvents()
    this.currentWeekStart = this.getWeekStart(new Date())

    // 如果有事件，默认显示第一个事件所在的月份
    this.$nextTick(() => {
      if (this.events.length > 0) {
        const firstEventDate = new Date(this.events[0].startDate)
        this.currentDate = new Date(firstEventDate.getFullYear(), firstEventDate.getMonth(), 1)
        console.log(`📅 日历显示月份: ${this.currentDate.getFullYear()}年${this.currentDate.getMonth() + 1}月`)
      }
    })
  }
}
</script>

<style scoped>
/* 基础面板 - 使用主题变量 */
.CalendarPanel {
  background: var(--theme-panel-bg);
  width: 100%;
  border-radius: 24px;
  box-shadow: 0 8px 32px var(--theme-panel-shadow);
  color: var(--theme-panel-text);
  border: 1px solid var(--theme-panel-border);
  position: relative;
  overflow: hidden;
  transition: var(--theme-transition-colors);
}

.CalendarPanel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--theme-primary), var(--theme-panel-bg), var(--theme-primary));
}

/* 紧凑模式 */
.compact-mode {
  padding: 1.25rem;
  cursor: pointer;
  transition: var(--theme-transition-colors);
}

.compact-mode:hover {
  background: var(--theme-surface-hover);
}

.month-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--theme-border-light);
}

.month-header .icon {
  width: 24px;
  height: 24px;
  color: var(--theme-primary);
}

.month-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--theme-primary);
  font-family: var(--gallery-font-mono);
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
  color: var(--theme-meta-text);
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
  background: var(--theme-surface-default);
  border-radius: 6px;
  font-size: 0.85rem;
  position: relative;
  transition: var(--theme-transition-colors);
  overflow: hidden;
}

.mini-day.other-month {
  opacity: 0.3;
}

.mini-day.today {
  background: var(--theme-nav-active-bg);
  border: 1px solid var(--theme-primary);
  color: var(--theme-primary);
  font-weight: 700;
}

.day-num {
  position: relative;
  z-index: 2;
}

.event-bars {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  display: flex;
  z-index: 1;
}

.event-bar {
  height: 100%;
  transition: height 0.2s ease;
}

.mini-day:hover .event-bar {
  height: 6px;
}

.today-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--theme-nav-active-bg);
  border-radius: 12px;
  border: 1px solid var(--theme-border-light);
}

.summary-label {
  font-size: 0.9rem;
  color: var(--theme-meta-text);
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--theme-primary);
  font-family: var(--gallery-font-mono);
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
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
}

.calendar-expanded-panel {
  position: relative;
  width: 95%;
  max-width: 1400px;
  height: 90vh;
  background: var(--theme-panel-bg);
  border-radius: 24px;
  box-shadow: 0 20px 60px var(--theme-shadow-xl);
  border: 1px solid var(--theme-panel-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.expanded-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--theme-border-light);
  background: var(--theme-surface-hover);
  flex-shrink: 0;
}

.expanded-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--theme-primary);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.expanded-header h2 svg {
  width: 28px;
  height: 28px;
}

.close-btn {
  background: var(--theme-surface-default);
  border: 1px solid var(--theme-border-light);
  border-radius: 12px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--theme-transition-colors);
  color: var(--theme-error);
}

.close-btn:hover {
  background: var(--theme-surface-hover);
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
  background: var(--theme-surface-default);
  border-radius: 16px;
  padding: 1rem;
  overflow: hidden;
  border: 1px solid var(--theme-border-light);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--theme-border-light);
}

.week-range {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--theme-primary);
  font-family: var(--gallery-font-mono);
}

.nav-btn {
  background: var(--theme-surface-default);
  border: 1px solid var(--theme-border-light);
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--theme-transition-colors);
  color: var(--theme-primary);
  font-size: 1.2rem;
}

.nav-btn:hover {
  background: var(--theme-nav-hover-bg);
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
  color: var(--theme-meta-text);
  font-family: var(--gallery-font-mono);
}

.day-column {
  display: flex;
  flex-direction: column;
  min-width: 100px;
}

.day-column.is-today {
  background: var(--theme-nav-active-bg);
  border-radius: 8px;
}

.day-header {
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: var(--theme-surface-hover);
  border-radius: 8px;
  margin-bottom: 8px;
  flex-shrink: 0;
  position: relative;
  border: 1px solid var(--theme-border-light);
}

.day-column.is-today .day-header {
  background: var(--theme-nav-active-bg);
  border-color: var(--theme-primary);
}

.day-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--theme-primary);
}

.day-date {
  font-size: 0.75rem;
  color: var(--theme-meta-text);
}

.day-count {
  position: absolute;
  top: 4px;
  right: 4px;
  background: var(--theme-primary);
  color: var(--theme-button-text);
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
  border-bottom: 1px solid var(--theme-border-light);
}

.timeline-event {
  position: absolute;
  border-radius: 6px;
  padding: 4px 6px;
  font-size: 0.75rem;
  color: var(--theme-button-text);
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 2px 8px var(--theme-shadow-md);
  transition: box-shadow 0.2s ease;
}

.timeline-event:hover {
  box-shadow: 0 4px 12px var(--theme-shadow-lg);
  z-index: 10;
}

.timeline-event.event-continuing {
  border-top: 2px dashed var(--theme-button-text);
  opacity: 0.85;
}

.timeline-event.event-first-day {
  border-left: 4px solid var(--theme-button-text);
}

.timeline-event.event-last-day {
  border-right: 4px solid var(--theme-button-text);
  opacity: 0.9;
}

.timeline-event.event-segmented {
  opacity: 0.7;
  border-top: 2px dotted var(--theme-button-text);
  border-bottom: 2px dotted var(--theme-button-text);
}

.event-duration {
  font-size: 0.65rem;
  opacity: 0.8;
  margin-top: 2px;
  font-weight: 600;
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
  background: var(--theme-surface-default);
  border-radius: 16px;
  padding: 1rem;
  overflow-y: auto;
  border: 1px solid var(--theme-border-light);
}

.calendar-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--theme-border-light);
}

.calendar-nav button {
  background: var(--theme-surface-default);
  border: 1px solid var(--theme-border-light);
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--theme-primary);
  font-size: 1.2rem;
  transition: var(--theme-transition-colors);
}

.calendar-nav button:hover {
  background: var(--theme-nav-hover-bg);
}

.calendar-month {
  font-size: 1rem;
  font-weight: 700;
  color: var(--theme-primary);
  font-family: var(--gallery-font-mono);
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
  color: var(--theme-meta-text);
  padding: 6px 0;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--theme-surface-hover);
  border: 1px solid var(--theme-border-light);
  border-radius: 8px;
  cursor: pointer;
  transition: var(--theme-transition-colors);
  position: relative;
  padding: 4px;
}

.calendar-day:hover {
  background: var(--theme-nav-hover-bg);
  border-color: var(--theme-primary);
}

.calendar-day.other-month {
  opacity: 0.3;
}

.calendar-day.today {
  background: var(--theme-nav-active-bg);
  border-color: var(--theme-primary);
  font-weight: 700;
  color: var(--theme-primary);
}

.calendar-day.selected {
  background: var(--theme-primary);
  color: var(--theme-button-text);
  border-color: var(--theme-primary);
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
  border-top: 1px solid var(--theme-border-light);
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
  overflow: hidden;
}

.selected-day-events h3 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: var(--theme-primary);
  flex-shrink: 0;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  overflow-y: auto;
  flex: 1;
  padding-right: 4px;
  padding-bottom: 8px;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--theme-surface-hover);
  border-radius: 8px;
  border: 1px solid var(--theme-border-light);
  transition: var(--theme-transition-colors);
  cursor: pointer;
}

.event-item:hover {
  background: var(--theme-nav-hover-bg);
  border-color: var(--theme-primary);
}

.event-color {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.event-info {
  flex: 1;
  min-width: 0;
}

.event-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--theme-panel-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-time-range {
  font-size: 0.75rem;
  color: var(--theme-meta-text);
}

@media (max-width: 1200px) {
  .expanded-content {
    grid-template-columns: 1fr;
  }

  .month-calendar {
    order: -1;
  }
}

@media (max-width: 768px) {
  .calendar-expanded-panel {
    width: 100%;
    height: 100vh;
    border-radius: 0;
  }
}

/* 自定义滚动条样式 */
.timeline-grid::-webkit-scrollbar,
.month-calendar::-webkit-scrollbar,
.events-list::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.timeline-grid::-webkit-scrollbar-track,
.month-calendar::-webkit-scrollbar-track,
.events-list::-webkit-scrollbar-track {
  background: var(--theme-surface-default);
  border-radius: 4px;
}

.timeline-grid::-webkit-scrollbar-thumb,
.month-calendar::-webkit-scrollbar-thumb,
.events-list::-webkit-scrollbar-thumb {
  background: var(--theme-border-medium);
  border-radius: 4px;
  transition: background 0.2s ease;
}

.timeline-grid::-webkit-scrollbar-thumb:hover,
.month-calendar::-webkit-scrollbar-thumb:hover,
.events-list::-webkit-scrollbar-thumb:hover {
  background: var(--theme-primary);
}

/* Firefox 滚动条样式 */
.timeline-grid,
.month-calendar,
.events-list {
  scrollbar-width: thin;
  scrollbar-color: var(--theme-border-medium) var(--theme-surface-default);
}
</style>
