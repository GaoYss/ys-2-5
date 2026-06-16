import { RotateCcw, Search } from "lucide-react";

export const defaultFilters = {
  class_id: "",
  teacher: "",
  room: "",
  date_from: "",
  date_to: "",
};

export function ScheduleFilter({
  classes = [],
  teachers = [],
  rooms = [],
  filters,
  onChange,
  onSearch,
  onReset,
  showSearch = true,
}) {
  function updateField(key, value) {
    onChange({ ...filters, [key]: value });
  }

  function handleSubmit(event) {
    event.preventDefault();
    onSearch?.(filters);
  }

  function handleReset() {
    onReset?.();
  }

  return (
    <form className="filter-panel" onSubmit={handleSubmit}>
      <div className="filter-row">
        <label>
          班级
          <select
            value={filters.class_id}
            onChange={(e) => updateField("class_id", e.target.value)}
          >
            <option value="">全部班级</option>
            {classes.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          教师
          <select
            value={filters.teacher}
            onChange={(e) => updateField("teacher", e.target.value)}
          >
            <option value="">全部教师</option>
            {teachers.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>

        <label>
          教室
          <select
            value={filters.room}
            onChange={(e) => updateField("room", e.target.value)}
          >
            <option value="">全部教室</option>
            {rooms.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>

        <label>
          开始日期
          <input
            type="date"
            value={filters.date_from}
            onChange={(e) => updateField("date_from", e.target.value)}
          />
        </label>

        <label>
          结束日期
          <input
            type="date"
            value={filters.date_to}
            onChange={(e) => updateField("date_to", e.target.value)}
          />
        </label>
      </div>

      <div className="filter-actions">
        <button
          type="button"
          className="secondary-action"
          onClick={handleReset}
        >
          <RotateCcw size={16} />
          重置
        </button>
        {showSearch && (
          <button type="submit" className="primary-action">
            <Search size={16} />
            查询
          </button>
        )}
      </div>
    </form>
  );
}
