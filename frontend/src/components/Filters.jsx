function Filters({ setFilter }) {
  return (
    <div className="mb-4 flex gap-4">
      <button
        onClick={() => setFilter("all")}
        className="px-4 py-2 bg-primary text-white rounded hover:bg-secondary transition"
      >
        Wszystkie
      </button>
      <button
        onClick={() => setFilter("active")}
        className="px-4 py-2 bg-primary text-white rounded hover:bg-secondary transition"
      >
        Aktywne
      </button>
      <button
        onClick={() => setFilter("paused")}
        className="px-4 py-2 bg-primary text-white rounded hover:bg-secondary transition"
      >
        Wstrzymane
      </button>
      <button
        onClick={() => setFilter("completed")}
        className="px-4 py-2 bg-primary text-white rounded hover:bg-secondary transition"
      >
        Zakończone
      </button>
    </div>
  );
}

export default Filters;
