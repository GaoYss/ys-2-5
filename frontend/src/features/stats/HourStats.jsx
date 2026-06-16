import { Lightbulb } from "lucide-react";
import { useEffect, useState } from "react";
import { SectionHeader } from "../../components/SectionHeader";
import { StatCard } from "../../components/StatCard";
import { ScheduleFilter, defaultFilters } from "../../components/ScheduleFilter";
import { api } from "../../services/api";

export function HourStats({ classes }) {
  const [filters, setFilters] = useState(defaultFilters);
  const [stats, setStats] = useState([]);
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

  async function loadStats(currentFilters = filters) {
    try {
      const data = await api.getHourStats(currentFilters);
      setStats(data.items || []);
      setSuggestions(data.suggestions || []);
    } catch (e) {
      console.warn("加载统计数据失败", e);
      setStats([]);
      setSuggestions([]);
    }
  }

  useEffect(() => {
    loadFilterOptions();
    loadStats();
  }, []);

  function handleFilterChange(nextFilters) {
    setFilters(nextFilters);
  }

  function handleFilterSearch(nextFilters) {
    loadStats(nextFilters);
  }

  function handleFilterReset() {
    setFilters(defaultFilters);
    loadStats(defaultFilters);
  }

  const totalPlanned = stats.reduce((sum, item) => sum + item.planned_hours, 0);
  const totalAttended = stats.reduce((sum, item) => sum + item.attended_hours, 0);
  const avgRate = stats.length
    ? Math.round(stats.reduce((sum, item) => sum + item.attendance_rate, 0) / stats.length)
    : 0;

  return (
    <section className="module">
      <div className="table-panel">
        <SectionHeader eyebrow="Filter" title="统计筛选" />
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

      <div className="metrics-grid">
        <StatCard label="已排课时" value={totalPlanned} helper="按课程时长汇总" />
        <StatCard label="有效出勤课时" value={totalAttended} helper="迟到与请假折算" />
        <StatCard label="平均出勤率" value={`${avgRate}%`} helper="按班级平均" />
      </div>

      <div className="table-panel">
        <SectionHeader eyebrow="Hours" title="班级课时统计" />
        {stats.length === 0 || stats.every((item) => item.planned_hours === 0) ? (
          <div className="empty-state">
            <div className="empty-icon">
              <Lightbulb size={28} />
            </div>
            <h3>没有匹配的统计数据</h3>
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
              <p>请调整筛选条件或先生成排课。</p>
            )}
          </div>
        ) : (
          <div className="responsive-table">
            <table>
              <thead>
                <tr>
                  <th>班级</th>
                  <th>学员数</th>
                  <th>已排课时</th>
                  <th>应到总课时</th>
                  <th>有效出勤课时</th>
                  <th>出勤率</th>
                </tr>
              </thead>
              <tbody>
                {stats.map((item) => (
                  <tr key={item.class_id}>
                    <td>
                      <strong>{item.class_name}</strong>
                    </td>
                    <td>{item.student_count}</td>
                    <td>{item.planned_hours}</td>
                    <td>{item.expected_total_hours}</td>
                    <td>{item.attended_hours}</td>
                    <td>
                      <span className="status-pill">{item.attendance_rate}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
