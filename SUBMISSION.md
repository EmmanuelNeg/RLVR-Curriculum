# SUBMISSION

# Excalidraw Curriculum Submission

**Author/Contributor:** Emmanuel Negedu // @EmmanuelNeg

---

# Overview

This submission contains three curriculum tasks designed to evaluate different aspects of the Claud opus 4.8 AI agent's ability to interact with Excalidraw using Browser-Use.

Rather than creating multiple variations of the same exercise, I intentionally designed tasks that probe different reasoning capabilities while progressively increasing the level of abstraction required from the model. Alongside the tasks themselves, I also extended parts of the evaluation framework to support richer grading logic and a more efficient development workflow.

The submitted tasks are:

1. **Circle Quadrant Transformation**
2. **Complete Drone Sketch**
3. **Group Chemical Equations**

Collectively, these tasks evaluate spatial reasoning, semantic drawing, planning, symbolic reasoning, visual organization, and classification.

---

# Thought Process

Before attempting to create new tasks, I wanted to understand how the existing framework worked rather than treating it as a black box.

My first step was setting up the repository locally, installing all dependencies, and familiarizing myself with the project structure. I spent time understanding how Excalidraw stores drawings, how `seed.json` files are generated, how Browser-Use interacts with the canvas, how calibration works, and how graders are evaluated.

To build this understanding, I explored the provided **yellow-circle-in-blue-box** example in detail. Instead of immediately creating new tasks, I studied:

* the curriculum structure
* task generation
* the grading SDK
* the calibration workflow
* Browser-Use interactions

This gave me a solid understanding of the evaluation pipeline and helped me identify both its strengths and its limitations.

After becoming comfortable with the framework, I experimented with several task ideas before settling on the final curriculum. Some concepts were discarded because they were either too easy for the model or too difficult to evaluate reliably.

One lesson quickly became apparent:

> Designing reliable graders was significantly more challenging than designing the tasks themselves.

As the complexity of the tasks increased, evaluation shifted away from simple coordinate comparisons toward semantic reasoning, structural validation, grouping, relative positioning, and tolerance-aware grading.

This experience reinforced an important principle of RLVR:

**The quality of an evaluation depends just as much on the grader as it does on the task itself.**

---

# Curriculum Thinking

Rather than creating three drawing exercises with increasing difficulty, I wanted each task to isolate a different reasoning capability.

The curriculum intentionally progresses from deterministic spatial reasoning toward higher-level semantic and symbolic reasoning.

| Task                           | Main Capability                                             
| ------------------------------ | -------------------------------------------------------------- 
| Circle Quadrant Transformation | Spatial reasoning, oject manipulation and geometric transformations                
| Complete Drone Sketch          | Semantic object completion, planning and freehand drawing      
| Group Chemical Equations       | Classification, symbolic reasoning and structured organization 

Each task probes a different aspect of model behavior, providing broader evaluation coverage while minimizing overlap.

---

# Generation Method

## Seed Generation

All tasks were generated programmatically using Python rather than manually editing Excalidraw exports.

Creating generators allowed the seeds to remain reproducible, easy to modify, and straightforward to recalibrate during development.

As I became more familiar with Excalidraw's internal JSON representation, I refined the generators to produce cleaner and more maintainable seed files.

---

## Grader Development

The graders went through several iterations.

My initial implementations relied heavily on coordinate comparisons. While this worked well for simple geometric tasks, it quickly became too brittle for more realistic scenarios involving freehand drawing and semantic completion.

I gradually shifted toward more robust grading strategies that evaluated:

* relative positioning
* spatial proximity
* grouping
* structural relationships
* text correctness
* semantic completeness
* tolerance-aware placement

The ***Complete Drone Sketch** task required the most iteration because there is no single "correct" drawing. Instead, the grader needed to determine whether the generated sketch contained the expected structural components while remaining flexible enough to accommodate natural variation in the model's drawings.

This was one of the most technically challenging aspects of the assignment.

---

# Framework Improvements

While building more sophisticated tasks, I found that the existing framework could benefit from additional reusable utilities and a smoother development workflow.

Rather than embedding helper logic directly into individual graders, I chose to improve the shared infrastructure where appropriate.

## SDK Extensions

The original SDK exposed the basic geometric properties required for simple shape-based grading. As the curriculum became more sophisticated, richer evaluation primitives became necessary.

I extended the SDK with several reusable capabilities.

### Text Support

Added support for:

* `text`
* `is_text()`
* `get_texts()`

This enabled graders to inspect labels and textual annotations.

---

### Line Support

Added support for:

* `points`
* `is_line()`
* `get_lines()`

This allows graders to evaluate drawn connections and line geometry.

---

### Freehand Drawing Support

Added support for:

* `is_freedraw()`
* `get_freedraws()`

This enabled graders to inspect sketches created with Excalidraw's pen tool rather than limiting evaluation to primitive shapes.

---

### Spatial Utilities

To support tolerance-aware grading, I implemented reusable spatial helper methods including:

* `center`
* `distance_to()`
* `is_near()`

These utilities allowed graders to compare relative positioning instead of relying solely on exact coordinate equality.

The result was a cleaner SDK and significantly simpler grader implementations.

---

## Runner Improvements

During development I encountered issues while dynamically importing custom grader modules.

To improve reliability, I updated the task runner so dynamically loaded graders are correctly registered with Python's module system before execution.

```python
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
```

Although this change is relatively small, it improved consistency during repeated calibration runs and ensured custom graders behaved reliably throughout development.

---

## Improving Observability During Development

As the tasks became more sophisticated, I found that inspecting only the final Excalidraw output was often insufficient for understanding why a model failed.

To improve debugging and calibration, I modified the Browser-Use execution so the agent's interactions could be observed live in the browser rather than running entirely in the background.

I also adjusted the browser interaction speed (click timing) to slow down the execution, making it easier to observe each action performed by the model.

Being able to watch the model interact with the canvas proved extremely valuable. It allowed me to identify issues that would have been difficult to infer from the final canvas alone, including:

* incorrect interaction sequences
* unnecessary clicks
* misplaced drawing operations
* navigation mistakes
* prompt interpretation errors

This significantly accelerated the iteration cycle while refining prompts and graders, particularly for the "Complete Drone Sketch" task where understanding the model's decision-making process was just as important as evaluating the final drawing.

---

# Task Analysis

## Task 1 — Circle Quadrant Transformation

### Capability Probed

* Spatial reasoning
* Coordinate transformations
* Relative positioning
* Object manipulation

### Design

The task evaluates whether the model can understand geometric relationships, positioning and correctly transform existing objects such as a circle, a triangle and a rectangle into different quadrants while preserving the intended layout.

Rather than simply creating new shapes, the model must reason about spatial transformations. 

The objective of this task was to create a seed state containing all the required elements positioned separately across the canvas, as shown in the reference image [Circle Quadrant - Seed](Images/circle-quadrant-seed.png). The seed consisted of four line elements, one large circle, three smaller circles, and one rectangle. Of the three smaller circles, one was intentionally created slightly smaller so that it could be contained within another circle during the task.

The task required the model to use the four existing line elements to form two perpendicular diameters across the large circle. One diameter was to be positioned horizontally and the other vertically, dividing the large circle into four distinct quadrants.

The expected final arrangement required the model to reposition the existing elements into the appropriate quadrants. In the first quadrant, the model was required to invert the triangle and position it within the quadrant. In the second quadrant, one of the existing circles was to be moved into the quadrant. In the third quadrant, two circles were to be repositioned so that the smaller circle was contained within the larger circle. In the fourth quadrant, the rectangle was to be positioned so that it extended slightly beyond the boundary of the large circle.

The task therefore evaluated the model's ability to interpret the spatial relationships between existing canvas elements, manipulate and reposition those elements, and correctly construct the intended quadrant based layout while preserving the required relationships between the shapes.


### Failure Mode / Callibration 


Claude Opus 4.8 generally understood the objective but occasionally produced slight positional inaccuracies after multiple transformations.

This highlighted the importance of tolerance-aware grading rather than strict coordinate equality.

The model scored 2 out of 5 during calibration. However, in most cases, the model performed well on the task and was able to complete the required spatial manipulations and arrange the elements in a way that was largely consistent with the intended outcome. Some of the failed attempts appeared to be influenced by discrepancies in the grader's evaluation rather than the model's actual performance. That said, the results still suggest that the task has room for improvement, particularly in refining the grading criteria to ensure that successful task completion is evaluated more accurately and consistently.

---

## Task 2 — Complete Drone Sketch

### Capability Probed

* Semantic reasoning
* Object completion
* Planning
* Freehand drawing
* Visual understanding
* Text labeling & generation.

### Design

The seed intentionally contains only the basic framework of an agricultural spraying drone. [Drone-sketch-seed](Images/drone-task-seed.png)

The model must infer the missing components, complete the sketch, and correctly annotate the finished system.
Unlike deterministic geometry tasks, there is no single correct drawing.
The engineering challenge therefore shifted from generation to evaluation.

### Failure Mode

This task consistently exposed weaknesses in the model's ability to complete and preserve existing elements in the seed. Although the model generally understood what an agricultural drone should look like, the final drawings varied significantly between runs, and it often created new elements instead of correctly using or preserving the existing ones.

In this run, the model did a good job of understanding the overall task and made a clear effort to complete the drone. It added the propellers, camera, landing legs, spray tank, spray boom, nozzles, and spray output. However, the grader only detected two of the four original drone arm lines, and it failed to recognize the spray boom, nozzles, and spray output that the model had attempted to add. The model also ran out of time before it could complete the required labels for the different components of the drone.

The biggest challenge with this task was designing a grader that could recognize valid solutions while still being flexible enough to account for differences in how the model completed the drawing. This was especially difficult because the model could produce something that was visually close to the expected result, but the grader would still fail to recognize some of the elements.

This task required the most refinement throughout development. The model scored 0 out of 5 during calibration, showing that there was still significant room for improvement in both the task and the grader, particularly around preserving the original seed elements and recognizing valid variations of the completed drawing.


---

## Task 3 — Group Chemical Equations

### Capability Probed

* Classification
* Symbolic reasoning
* Domain knowledge
* Structured organization

### Design

Unlike the previous tasks, this exercise focuses primarily on reasoning rather than drawing. Althought the model was asked to draw a circle inbetween the label boxes as an attempt to stun it. 

The model must correctly classify chemical equations into four reaction categories while arranging them into a clear visual structure (rectangluar boxes with labels)

The task therefore combines scientific reasoning with visual organization as well as the symetric object alignment.

### Failure Mode

The model performed exceptionally well on this task and consistently demonstrated a strong understanding of the required spatial organization. The graphical layout was well structured, and the model was able to correctly organize the elements according to the task requirements.

The model actually exceeded my expectations throughout the development and calibration process. Regardless of how many iterations I tried, it consistently completed the task successfully and ultimately passed all 5 out of 5 calibration attempts. This suggests that the task instructions were clear enough for the model to understand the intended outcome and that the grading criteria were effective in recognizing valid solutions.

Overall, I did not observe any significant failure mode during calibration. The model's consistent 5 out of 5 performance suggests that the task was relatively robust and that the model was able to reliably execute the required actions.


---

# Scaling the Curriculum

I would make the shift toward **real world interaction tasks** the central point, while keeping the parameterized pipeline as a supporting idea:

If this curriculum were expanded further, I would place greater emphasis on real world interaction tasks, such as website navigation, form filling, web applications, and desktop manipulation, rather than relying heavily on Excalidraw. I believe models can become familiar with the patterns and workflows of a specific environment like Excalidraw, whereas real world applications would provide a broader and more challenging test of their ability to reason and interact with unfamiliar interfaces.

I would also move toward a parameterized task generation pipeline, where task families could be created by varying object types, layouts, spatial constraints, transformations, distractors, and grading tolerances. Each generated task could automatically include its prompt, reproducible seed, deterministic grader, and calibration metadata. This would make it possible to scale the curriculum from a small set of manually designed tasks to hundreds or thousands of diverse tasks while maintaining consistency and reducing manual effort.

---

# Results

The submitted curriculum successfully demonstrates progressively more complex reasoning tasks across multiple capability domains.

Throughout calibration, both the generators and graders required several iterations before achieving acceptable robustness.

The ***Complete Drone Sketch** task required the greatest amount of refinement due to the inherent variability of freehand drawing and semantic completion.

One of the most important outcomes of this project was recognizing that robust evaluation infrastructure often requires more engineering effort than task creation itself.


---

# Lessons Learned

Several key lessons emerged during this project.

First, creating interesting tasks is only one component of curriculum design. Producing reliable, reusable, and maintainable graders is equally important.

Second, extending shared infrastructure is often more valuable than embedding task-specific logic into individual graders. The SDK improvements reduced duplication, simplified grader implementations, and made future task development easier.

Third, improving observability during development dramatically accelerated debugging. Being able to watch the model interact with Excalidraw in real time provided insights that would have been difficult to obtain from screenshots or final outputs alone.

The model is exceptionally brilliant but still prone to making mistakes. 

Finally, curriculum diversity matters. Effective RLVR evaluations should probe multiple reasoning capabilities rather than repeatedly measuring the same behavior with minor variations. As well as explore different environment besides Excalidraw. 

---

# Conclusion

This assignment provided valuable experience in designing RLVR evaluation tasks, building deterministic graders, extending shared evaluation infrastructure, and iteratively refining calibration workflows.

Beyond creating three curriculum tasks, I also:

* Extended the evaluation SDK with reusable grading primitives.
* Improved dynamic grader loading within the task runner.
* Enhanced the Browser-Use development workflow by enabling live execution and slowing interaction speed for easier debugging.
* Iteratively refined graders to balance determinism with tolerance-aware evaluation.

Overall, the project reinforced that scalable AI evaluation is fundamentally an engineering problem. Well-designed graders, reusable infrastructure, and thoughtful curriculum design are just as important as the tasks themselves, and together they form the foundation of robust reinforcement learning evaluation systems. Carrying out AI evaluations in other environments will be really interesting and easier to evaluate programtically. 

