"""
CDC Developmental Milestones Extractor

Extracts CDC "Learn the Signs. Act Early" milestones into structured JSON format.
Data source: CDC.gov official developmental milestone checklists (2022 updated standards)

Domains:
- Social/Emotional
- Language/Communication  
- Cognitive (Learning, Thinking, Problem-Solving)
- Movement/Physical Development (Gross Motor + Fine Motor)
"""

import json
from pathlib import Path
from typing import List, Dict


class CDCMilestoneExtractor:
    """Extract and structure CDC developmental milestones."""
    
    def __init__(self, output_dir: str = "parsed_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # CDC Milestone data structure (2022 updated)
        # Source: https://www.cdc.gov/ncbddd/actearly/milestones/index.html
        self.milestones = self._load_cdc_data()
    
    def _load_cdc_data(self) -> Dict[int, Dict[str, List[str]]]:
        """
        Load CDC milestone data by age.
        
        Returns structured milestones by age checkpoint and domain.
        """
        return {
            2: {  # 2 months
                "Social/Emotional": [
                    "Calms down when spoken to or picked up",
                    "Looks at your face",
                    "Seems happy to see you when you walk up to them",
                    "Smiles when you talk to or smile at them"
                ],
                "Language/Communication": [
                    "Makes sounds other than crying",
                    "Reacts to loud sounds"
                ],
                "Cognitive": [
                    "Watches you as you move",
                    "Looks at a toy for several seconds"
                ],
                "Movement/Physical": [
                    "Holds head up when on tummy",
                    "Moves both arms and both legs",
                    "Briefly opens fingers when hands are relaxing"
                ]
            },
            4: {  # 4 months
                "Social/Emotional": [
                    "Smiles on their own to get your attention",
                    "Chuckles (not yet a full laugh) when you try to make them laugh",
                    "Looks at you, moves, or makes sounds to get or keep your attention"
                ],
                "Language/Communication": [
                    "Makes sounds like 'oooo', 'aahh' (cooing)",
                    "Makes sounds back when you talk to them",
                    "Turns head towards the sound of your voice"
                ],
                "Cognitive": [
                    "If hungry, opens mouth when they see breast or bottle",
                    "Looks at their hands with interest"
                ],
                "Movement/Physical": [
                    "Holds head steady without support when being held",
                    "Holds a toy when you put it in their hand",
                    "Uses their arm to swing at toys",
                    "Brings hands to mouth",
                    "Pushes up onto elbows/forearms when on tummy"
                ]
            },
            6: {  # 6 months
                "Social/Emotional": [
                    "Knows familiar people",
                    "Likes to look at self in a mirror",
                    "Laughs"
                ],
                "Language/Communication": [
                    "Takes turns making sounds with you",
                    "Blows 'raspberries' (sticks tongue out and blows)",
                    "Makes squealing noises"
                ],
                "Cognitive": [
                    "Puts things in their mouth to explore them",
                    "Reaches to grab a toy they want",
                    "Closes lips to show they don't want more food"
                ],
                "Movement/Physical": [
                    "Rolls from tummy to back",
                    "Pushes up with straight arms when on tummy",
                    "Leans on hands to support self when sitting"
                ]
            },
            9: {  # 9 months
                "Social/Emotional": [
                    "Is shy, clingy, or fearful around strangers",
                    "Shows several facial expressions, like happy, sad, angry, and surprised",
                    "Looks when you call their name",
                    "Reacts when you leave (looks, reaches for you, or cries)",
                    "Smiles or laughs when you play peek-a-boo"
                ],
                "Language/Communication": [
                    "Makes a lot of different sounds like 'mamamama' and 'babababa'",
                    "Lifts arms up to be picked up"
                ],
                "Cognitive": [
                    "Looks for objects when dropped out of sight (like their spoon or toy)",
                    "Bangs two things together"
                ],
                "Movement/Physical": [
                    "Gets to a sitting position by themselves",
                    "Moves things from one hand to the other hand",
                    "Uses fingers to 'rake' food towards themselves",
                    "Sits without support"
                ]
            },
            12: {  # 12 months (1 year)
                "Social/Emotional": [
                    "Plays games with you, like pat-a-cake"
                ],
                "Language/Communication": [
                    "Waves 'bye-bye'",
                    "Calls a parent 'mama' or 'dada' or another special name",
                    "Understands 'no' (pauses briefly or stops when you say it)"
                ],
                "Cognitive": [
                    "Puts something in a container, like a block in a cup",
                    "Looks for things they see you hide, like a toy under a blanket"
                ],
                "Movement/Physical": [
                    "Pulls up to stand",
                    "Walks, holding on to furniture ('cruising')",
                    "Drinks from a cup without a lid, as you hold it",
                    "Picks things up between thumb and pointer finger, like small bits of food"
                ]
            },
            15: {  # 15 months
                "Social/Emotional": [
                    "Copies other children while playing, like taking toys out of a container when another child does",
                    "Shows you an object they like",
                    "Claps when excited",
                    "Hugs stuffed doll or other toy",
                    "Shows you affection (hugs, cuddles, or kisses you)"
                ],
                "Language/Communication": [
                    "Tries to say one or two words besides 'mama' or 'dada', like 'ba' for ball or 'da' for dog",
                    "Looks at a familiar object when you name it",
                    "Follows directions given with both a gesture and words. For example, they give you a toy when you hold out your hand and say, 'Give me the toy.'",
                    "Points to ask for something or to get help"
                ],
                "Cognitive": [
                    "Tries to use things the right way, like a phone, cup, or book",
                    "Stacks at least two small objects, like blocks"
                ],
                "Movement/Physical": [
                    "Takes a few steps on their own",
                    "Uses fingers to feed themselves some food"
                ]
            },
            18: {  # 18 months
                "Social/Emotional": [
                    "Moves away from you, but looks to make sure you are close by",
                    "Points to show you something interesting",
                    "Puts hands out for you to wash them",
                    "Looks at a few pages in a book with you",
                    "Helps you dress them by pushing arm through sleeve or lifting up foot"
                ],
                "Language/Communication": [
                    "Tries to say three or more words besides 'mama' or 'dada'",
                    "Follows one-step directions without any gestures, like giving you the toy when you say, 'Give it to me.'"
                ],
                "Cognitive": [
                    "Copies you doing chores, like sweeping with a broom",
                    "Plays with toys in a simple way, like pushing a toy car"
                ],
                "Movement/Physical": [
                    "Walks without holding on to anyone or anything",
                    "Scribbles",
                    "Drinks from a cup without a lid and may spill sometimes",
                    "Feeds themselves with their fingers",
                    "Tries to use a spoon",
                    "Climbs on and off a couch or chair without help"
                ]
            },
            24: {  # 24 months (2 years)
                "Social/Emotional": [
                    "Notices when others are hurt or upset, like pausing or looking sad when someone is crying",
                    "Looks at your face to see how to react in a new situation"
                ],
                "Language/Communication": [
                    "Points to things in a book when you ask, like 'Where is the bear?'",
                    "Says at least two words together, like 'More milk'",
                    "Points to at least two body parts when you ask them to show you",
                    "Uses more gestures than just waving and pointing, like blowing a kiss or nodding yes"
                ],
                "Cognitive": [
                    "Holds something in one hand while using the other hand; for example, holding a container and taking the lid off",
                    "Tries to use switches, knobs, or buttons on a toy",
                    "Plays with more than one toy at the same time, like putting toy food on a toy plate"
                ],
                "Movement/Physical": [
                    "Kicks a ball",
                    "Runs",
                    "Walks (not climbs) up a few stairs with or without help",
                    "Eats with a spoon"
                ]
            },
            30: {  # 30 months (2.5 years)
                "Social/Emotional": [
                    "Plays next to other children and sometimes plays with them",
                    "Shows you what they can do by saying, 'Look at me!'",
                    "Follows simple routines when told, like helping to pick up toys when you say, 'It's clean-up time.'"
                ],
                "Language/Communication": [
                    "Says about 50 words",
                    "Says two or more words, with one action word, like 'Doggie run'",
                    "Names things in a book when you point and ask, 'What is this?'",
                    "Says words like 'I,' 'me,' or 'we'"
                ],
                "Cognitive": [
                    "Uses things to pretend, like feeding a block to a doll as if it were food",
                    "Shows simple problem-solving skills, like standing on a small stool to reach something",
                    "Follows two-step instructions like 'Put the toy down and close the door'",
                    "Shows they know at least one color, like pointing to a red crayon when you ask, 'Which one is red?'"
                ],
                "Movement/Physical": [
                    "Uses hands to twist things, like turning doorknobs or unscrewing lids",
                    "Takes some clothes off by themselves, like loose pants or an open jacket",
                    "Jumps off the ground with both feet",
                    "Turns book pages, one at a time, when you read to them"
                ]
            },
            36: {  # 36 months (3 years)
                "Social/Emotional": [
                    "Calms down within 10 minutes after you leave them, like at a childcare drop off",
                    "Notices other children and joins them to play"
                ],
                "Language/Communication": [
                    "Talks with you in conversation using at least two back-and-forth exchanges",
                    "Asks 'who,' 'what,' 'where,' or 'why' questions, like 'Where is mommy/daddy?'",
                    "Says what action is happening in a picture or book when asked, like 'running,' 'eating,' or 'playing'",
                    "Says first name, when asked",
                    "Talks well enough for others to understand, most of the time"
                ],
                "Cognitive": [
                    "Draws a circle, when you show them how",
                    "Avoids touching hot objects, like a stove, when you warn them"
                ],
                "Movement/Physical": [
                    "Strings items together, like large beads or macaroni",
                    "Puts on some clothes by themselves, like loose pants or a jacket",
                    "Uses a fork"
                ]
            }
        }
    
    def extract_to_json(self) -> List[Dict]:
        """
        Convert CDC milestones to structured JSON format.
        
        Returns:
            List of milestone dictionaries
        """
        structured_milestones = []
        
        for age_months, domains in self.milestones.items():
            for domain, milestones in domains.items():
                for milestone_text in milestones:
                    # Map CDC domains to our domain categories
                    mapped_domain = self._map_domain(domain)
                    
                    milestone_entry = {
                        "source": "CDC Learn the Signs. Act Early",
                        "domain": mapped_domain,
                        "age_checkpoint": age_months,
                        "age_min": self._calculate_age_min(age_months),
                        "age_max": self._calculate_age_max(age_months),
                        "milestone_text": milestone_text,
                        "original_domain": domain  # Preserve CDC's original categorization
                    }
                    
                    structured_milestones.append(milestone_entry)
        
        return structured_milestones
    
    def _map_domain(self, cdc_domain: str) -> str:
        """
        Map CDC domain names to our system's domain categories.
        
        Args:
            cdc_domain: Original CDC domain name
            
        Returns:
            Mapped domain name
        """
        domain_mapping = {
            "Social/Emotional": "Social Interaction",
            "Language/Communication": "Language",
            "Cognitive": "Self-Directed Learning",
            "Movement/Physical": "Gross Motor"  # We'll split fine motor where appropriate
        }
        
        return domain_mapping.get(cdc_domain, cdc_domain)
    
    def _calculate_age_min(self, checkpoint: int) -> int:
        """Calculate minimum age for milestone appearance."""
        # Allow 1-2 months before checkpoint
        buffer = 2 if checkpoint > 12 else 1
        return max(0, checkpoint - buffer)
    
    def _calculate_age_max(self, checkpoint: int) -> int:
        """Calculate maximum age for milestone mastery."""
        # Allow 2-3 months after checkpoint
        buffer = 3 if checkpoint > 12 else 2
        return checkpoint + buffer
    
    def save_json(self, filename: str = "cdc_milestones_structured.json"):
        """Save structured milestones to JSON file."""
        structured_data = self.extract_to_json()
        
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Extracted {len(structured_data)} CDC milestones")
        print(f"✓ Saved to: {output_path}")
        
        # Print summary
        domains = {}
        for milestone in structured_data:
            domain = milestone['domain']
            domains[domain] = domains.get(domain, 0) + 1
        
        print("\nDomain distribution:")
        for domain, count in sorted(domains.items()):
            print(f"  {domain}: {count} milestones")
        
        return output_path


def main():
    """Extract CDC milestones."""
    print("="*80)
    print("CDC Developmental Milestones Extraction")
    print("="*80)
    print("\nSource: CDC 'Learn the Signs. Act Early' (2022 Updated Standards)")
    print("Age checkpoints: 2, 4, 6, 9, 12, 15, 18, 24, 30, 36 months\n")
    
    extractor = CDCMilestoneExtractor()
    output_path = extractor.save_json()
    
    print("\n" + "="*80)
    print("✅ CDC Milestone Extraction Complete")
    print("="*80)
    print(f"\nNext step: Run load_structured_data.py to merge with existing knowledge base")


if __name__ == "__main__":
    main()
