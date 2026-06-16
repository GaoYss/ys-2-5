import { CalendarPlus, Lightbulb } from "lucide-react";
import { useEffect, useState } from "react";
import { SectionHeader } from "../../components/SectionHeader";
import { ScheduleFilter, defaultFilters } from "../../components/ScheduleFilter";
import { api } from "../../services/api";

export function ScheduleBoard({ classes, courses, onGenerate, onScheduleChange }) {
  const [genClassId, setGenClassId] = useState("");
  const [days, setDays] = useState(8);

  const [filters, setFilters] = useState(defaultFilters);
  const [schedule, setSchedule] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [rooms, setRooms] = useState([]);

  async function loadFilterOptions() {
    try {
      const opts = await api.getScheduleFilterOptions();
      setTeachers(opts.teachers || []);
      setRooms(opts.rooms || []);
    } catch (e) {
      console.warn("加载筛选选项失败", e);
    }
  }

  async function loadSchedule(currentFilters = filters) {
    try {
      const data = await api.getSchedule(currentFilters);
      setSchedule(data.items || []);
      setSuggestions(data.suggestions || []);
      onScheduleChange?.(data.items || []);
    } catch (e) {
      console.warn("加载课程表失败", e);
      setSchedule([]);
      setSuggestions([]);
    }
  }

  useEffect(() => {
    loadFilterOptions();
    loadSchedule();
  }, []);

  async function submitGenerate(event) {
    event.preventDefault();
    await onGenerate({ class_id: genClassId || undefined, days });
    loadFilterOptions();
    loadSchedule();
  }

  function handleFilterChange(nextFilters) {
    setFilters(nextFilters);
  }

  function handleFilterSearch(nextFilters) {
    loadSchedule(nextFilters);
  }

  function handleFilterReset() {
    setFilters(defaultFilters);
    loadSchedule(defaultFilters);
  }

  return (
    <section className="module">
      <form className="toolbar-panel" onSubmit={submitGenerate}>
        <label>
          排课班级
          <select value={genClassId} onChange={(event) => setGenClassId(event.target.value)}>
            <option value="">全部班级</option>
            {classes.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          生成课次数
          <input
            min="1"
            max="30"
            type="number"
            value={days}
            onChange={(event) => setDays(Number(event.target.value))}
          />
        </label>
        <button className="primary-action" type="submit">
          <CalendarPlus size={18} />
          自动生成课程表
        </button>
      </form>

      <div className="table-panel">
        <SectionHeader eyebrow="Filter" title="课程筛选" />
        <ScheduleFilter
          classes={classes}
          teachers={teachers}
          rooms={rooms}
          filters={filters}
          onChange={handleFilterChange}
          onSearch={handleFilterSearch}
          onReset={handleFilterReset}
        />
      </div>

      <div className="table-panel">
        <SectionHeader eyebrow="Schedule" title="课程表" />
        {schedule.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              <Lightbulb size={28} />
            </div>
            <h3>没有找到匹配的课程</h3>
            {suggestions.length > 0 ? (
              <ul className="suggestions">
                {suggestions.map((s, idx) => (
                  <li key={idx} className={`suggestion suggestion-${s.type}`}>
                    <span className="suggestion-label">建议</span>
                    {s.message}
                  </li>
                ))}
              </ul>
            ) : (
              <p>请调整筛选条件或先生成课程。</p>
            )}
          </div>
        ) : (
          <div className="schedule-grid">
            {schedule.map((session) => (
              <article className="schedule-card" key={session.id}>
                <span>{session.date}</span>
                <h3>{session.course_title}</h3>
                <p>{session.class_name}</p>
                <div>
                  <small>{session.time}</small>
                  <small>{session.room}</small>
                  <small>{session.teacher}</small>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>

      <div className="table-panel">
        <SectionHeader eyebrow="Courses" title="课程库" />
        <div className="course-tags">
          {courses.map((course) => (
            <span key={course.id}>
              {course.title} · {course.duration}课时 · {course.category}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
