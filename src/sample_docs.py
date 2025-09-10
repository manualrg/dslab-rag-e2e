from langchain.schema import Document


uuids = ['2690cf82-ebfd-48bc-bd52-c61a595a212a',
 '0e8f454e-3ebf-434b-a7cf-26489695bcd0']
docs = [
    Document(
        page_content="John J. Hopfield and Geoffrey Hinton received the Nobel Prize in Physics in 2024 for their groundbreaking work on artificial neural networks, a foundation of modern AI. Hopfield developed an associative memory model in the 1980s that allows networks to store and reconstruct patterns. Building on this, Hinton developed the Boltzmann machine, which uses statistical physics principles to recognize and classify data. These pioneering contributions are essential for today's machine learning technologies, enhancing applications from medical imaging to material science.",
        metadata={"source": "wikipedia", "topic": "Physics"}
    ),
    Document(
        page_content="In Chemistry, David Baker, Demis Hassabis, and John Jumper were honored win Nobel Prize in 2024 for their breakthroughs in protein structure prediction. Baker’s work in computational protein design enables the creation of novel proteins, while Hassabis and Jumper, known for their work with DeepMind's AlphaFold, developed an AI that accurately predicts protein structures—a long-standing challenge in biology. This advancement could lead to transformative applications in drug development and synthetic biology.",
        metadata={"source": "wikipedia", "topic": "Chemistry"}
    ),
]