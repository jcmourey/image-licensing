const TailwindTest = () => (
  <div className="mb-6 border-4 border-red-500 p-4">
    <h2 className="text-lg font-semibold mb-2 text-red-600">Tailwind CSS Test (Should have red border)</h2>
    <div className="p-4 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 text-white rounded-lg shadow-xl">
      <p className="font-bold text-xl">This element uses Tailwind classes</p>
      <p className="text-sm mt-1">If you can see this colorful gradient background, Tailwind is working!</p>
      <div className="flex space-x-4 mt-4">
        <button className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors">
          Blue Button
        </button>
        <button className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors">
          Green Button
        </button>
        <button className="px-4 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600 transition-colors">
          Purple Button
        </button>
      </div>
    </div>
    <div className="mt-4 grid grid-cols-3 gap-4">
      <div className="bg-pink-200 p-3 rounded-lg text-center">Pink</div>
      <div className="bg-teal-200 p-3 rounded-lg text-center">Teal</div>
      <div className="bg-orange-200 p-3 rounded-lg text-center">Orange</div>
    </div>
  </div>
);

export default TailwindTest;