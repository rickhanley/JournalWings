class ShowHeader:
    def __init__(self):
          pass
    # https://www.asciiart.eu/text-to-ascii-art

    def rgb(self, r, g, b, text):
        return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

    def show_header(self):
        header = r"""
    ╔════════════════════════════════════════════════════════════════════════╗
                      __                             __          
                     / /___  __  ___________  ____ _/ /          
                __  / / __ \/ / / / ___/ __ \/ __ `/ /           
               / /_/ / /_/ / /_/ / /  / / / / /_/ / /            
               \____/\____/\__,_/_/  /_/ /_/\__,_/_/             
                                     _       ___                 
                                    | |     / (_)___  ____ ______
                                    | | /| / / / __ \/ __ `/ ___/
                                    | |/ |/ / / / / / /_/ (__  ) 
                                    |__/|__/_/_/ /_/\__, /____/  
                                                   /____/                                                           
                                    Journal automation                     

    ╚════════════════════════════════════════════════════════════════════════╝
    """
        lines = header.splitlines()
        total = len(lines)

        # colour stops
        pink   = (255, 20, 147)
        orange = (255, 140, 0)
        blue   = (0, 191, 255)

        for i, line in enumerate(lines):
            t = i / max(1, total - 1)

            if t <= 0.5:
                # pink → orange
                local_t = t / 0.5
                r = int(pink[0] + (orange[0] - pink[0]) * local_t)
                g = int(pink[1] + (orange[1] - pink[1]) * local_t)
                b = int(pink[2] + (orange[2] - pink[2]) * local_t)
            else:
                # orange → blue
                local_t = (t - 0.5) / 0.5
                r = int(orange[0] + (blue[0] - orange[0]) * local_t)
                g = int(orange[1] + (blue[1] - orange[1]) * local_t)
                b = int(orange[2] + (blue[2] - orange[2]) * local_t)

            print(self.rgb(r, g, b, line))
