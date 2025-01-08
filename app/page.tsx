'use client';

export default function Home() {
  const steps = [
    {
      title: "Content Acquisition",
      description: "Fetch daily news or input your own content for the podcast.",
      href: "/content-acquisition"
    },
    {
      title: "Content Outline",
      description: "Generate an outline and questions based on the content.",
      href: "/content-outline"
    },
    {
      title: "Podcast Generation",
      description: "Create the podcast script based on the outline and questions.",
      href: "/podcast-generation"
    },
    {
      title: "Audio Generation",
      description: "Convert the podcast script into audio.",
      href: "/audio-generation"
    }
  ];

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8 text-center">AI Podcast Tool</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {steps.map((step, index) => (
            <a 
              key={index} 
              href={step.href}
              className="block bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="mb-4">
                <h2 className="text-xl font-semibold">Step {index + 1}: {step.title}</h2>
              </div>
              <div>
                <p className="text-gray-600">{step.description}</p>
              </div>
            </a>
          ))}
        </div>
      </div>
    </main>
  );
}

