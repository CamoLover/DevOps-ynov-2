db = db.getSiblingDB('blog_db');

db.createCollection("posts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "content", "author", "createdAt"],
      properties: {
        title: {
          bsonType: "string",
          description: "Le titre doit être une chaîne et est requis"
        },
        content: {
          bsonType: "string",
          description: "Le contenu doit être une chaîne et est requis"
        },
        author: {
          bsonType: "string",
          description: "L'auteur doit être une chaîne et est requis"
        },
        createdAt: {
          bsonType: "date",
          description: "La date de création doit être une date et est requise"
        },
        tags: {
          bsonType: "array",
          description: "Les tags doivent être un tableau"
        }
      }
    }
  }
});

db.posts.insertMany([
  {
    title: "Introduction à Docker",
    content: "Docker est une plateforme de conteneurisation qui permet d'empaqueter des applications...",
    author: "Alice",
    createdAt: new Date("2024-01-15"),
    tags: ["docker", "devops", "conteneurisation"]
  },
  {
    title: "MongoDB et NoSQL",
    content: "MongoDB est une base de données NoSQL orientée documents qui offre flexibilité et scalabilité...",
    author: "Bob",
    createdAt: new Date("2024-02-20"),
    tags: ["mongodb", "nosql", "database"]
  },
  {
    title: "FastAPI pour les APIs modernes",
    content: "FastAPI est un framework Python moderne pour créer des APIs avec de hautes performances...",
    author: "Charlie",
    createdAt: new Date("2024-03-10"),
    tags: ["python", "fastapi", "api"]
  },
  {
    title: "Docker Compose et orchestration",
    content: "Docker Compose permet d'orchestrer plusieurs conteneurs et de gérer leurs dépendances...",
    author: "Diana",
    createdAt: new Date("2024-04-05"),
    tags: ["docker-compose", "orchestration", "devops"]
  },
  {
    title: "Architecture hybride SQL/NoSQL",
    content: "Combiner SQL et NoSQL dans une même architecture permet de tirer parti des avantages de chaque paradigme...",
    author: "Eve",
    createdAt: new Date("2024-04-15"),
    tags: ["architecture", "sql", "nosql", "hybrid"]
  }
]);
